
import { Paper, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography } from '@mui/material';
import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';
import Table from '@mui/material/Table';
import { DateTimePicker } from '@mui/x-date-pickers';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import * as React from 'react';
import runService from '../../run.service.tsx';
import checkService from '../../check.service.tsx';
import { withRouter } from '../../withRouter';
import dayjs from 'dayjs';
import Chart from "react-apexcharts";


const columns: GridColDef[] = [
  {
    field: 'timestamp',
    headerName: 'Timestamp',
    width: 200
  },
  {
    field: 'result',
    headerName: 'Result',
    width: 400,
    valueGetter: (data) => {
      if (data.row.result === 'SUCCESS') {
        return 'Success'
      } else if (data.row.result === 'FAILED') {
        return 'Failed';
      } else if (data.row.result === 'INTERNAL_ERROR') {
        return 'Internal error';
      } else if (data.row.result === 'TIMEOUT') {
        return 'Timed out'
      } else if (data.row.result === 'RUNNING') {
        return 'Running';
      } else if (data.row.result === 'NOT_RUN') {
        return 'Not run'
      }
      return 'Unknown status'
    }
  }
];

class CheckView extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      runs: [],
      detailsRows: [],
      manualTriggerState: null,
      manualTriggerId: null,
      fromDate: dayjs().subtract(7, 'day').set('second', 0).set('minute', 0).set('hour', 0),
      toDate: dayjs().set('second', 59).set('minute', 59).set('hour', 23),
      heatmapData: [],
    };
    this.retrieveRuns = this.retrieveRuns.bind(this);
    this.getRunDetails = this.getRunDetails.bind(this);
    this.onRowClick = this.onRowClick.bind(this);
    this.triggerRun = this.triggerRun.bind(this);
    this.checkManualRunStatus = this.checkManualRunStatus.bind(this);
    this.setFromDate = this.setFromDate.bind(this);
    this.setToDate = this.setToDate.bind(this);
  }

  componentDidMount() {
    document.title = `JMon - ${this.props.match.checkName} - ${this.props.match.environmentName}`;
    this.retrieveRuns();
    this.getRunDetails();
  }

  setFromDate(newDate) {
    this.setState((state) => Object.assign({}, state, {fromDate: newDate}), () => {
      this.retrieveRuns();
    });
  }
  setToDate(newDate) {
    this.setState((state) => Object.assign({}, state, {toDate: newDate}), () => {
      this.retrieveRuns();
    });
  }

  retrieveRuns() {
    new runService().listByCheck(
      this.props.match.checkName,
      this.props.match.environmentName,
      this.state.fromDate,
      this.state.toDate,
    ).then((runRes) => {
      this.setState((state) => Object.assign(
        {},
        state,
        {
          runs: Object.keys(runRes.data).map((key) => {return {timestamp: key, result: runRes.data[key]}}),
        })
      );
    });

    new checkService().getHeatmapData(
      this.props.match.checkName,
      this.props.match.environmentName,
      this.state.fromDate,
      this.state.toDate,
    ).then((heatmapDataRes) => {
      this.setState((state) => Object.assign(
        {},
        state,
        {
          heatmapData: [
            {
              name: "Uptime",
              data: heatmapDataRes.data
            }
          ]
        }));
    })
  }

  triggerRun() {
    new runService().triggerRun(this.props.match.checkName, this.props.match.environmentName).then((triggerRes) => {
      this.setState((state) => {
        return Object.assign({}, {...state, manualTriggerState: 'SCHEDULING', manualRunId: triggerRes.data.id});
      });

      setTimeout(this.checkManualRunStatus, 1000, [triggerRes.data.id]);
    });
  }

  checkManualRunStatus(triggerId) {
    // Check manual trigger from ID
    new runService().getManualTriggerStatus(
      this.props.match.checkName,
      this.props.match.environmentName,
      triggerId
    ).then((triggerStatusRes) => {
      // If ID is present, redirect user to run
      if (triggerStatusRes.data.id) {
        this.props.navigate(`/checks/${this.props.match.checkName}/environments/${this.props.match.environmentName}/runs/${triggerStatusRes.data.id}`);
      } else {
        this.setState((state) => {return Object.assign({}, {...state, manualTriggerState: triggerStatusRes.data.state})});
        // Otherwise, update status and re-schedule check
        setTimeout(this.checkManualRunStatus, 1000, [triggerId]);
      }
    })
  }

  getRunDetails() {
    new checkService().getByNameAndEnvironment(
      this.props.match.checkName,
      this.props.match.environmentName
    ).then((checkRes) => {
      this.setState((state) => {
        return {
          runs: state.runs,
          detailsRows: [
            {name: 'Name', value: this.props.match.checkName},
            {name: 'Environment', value: this.props.match.environmentName},
            {name: 'State', value: checkRes.data.enable ? 'Enabled' : 'Disabled'},
            {name: 'Interval', value: checkRes.data.calculated_interval + 's ' + (!checkRes.data.interval ? '(default)' : '')},
            {name: 'Timeout', value: checkRes.data.calculated_timeout + 's ' + (!checkRes.data.timeout ? '(default)' : '')},
            {name: 'Client Pinning', value: checkRes.data.client ? checkRes.data.client : 'None'},
            {name: 'Supported Clients', value: checkRes.data.supported_clients.join(', ')},
            {name: 'Number of Steps', value: checkRes.data.step_count}
          ]
        }
      })
    })
  }

  onRowClick(val: any) {
    this.props.navigate(`/checks/${this.props.match.checkName}/environments/${this.props.match.environmentName}/runs/${val.row.timestamp}`);
  }

  render() {
    return (
      <Container  maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Grid container spacing={3}>
          <Grid
            item
            xs={12} md={8} lg={6} xl={4}
          >
            <TableContainer component={Paper}>
              <Table sx={{ minWidth: 250 }} aria-label="Check details">
                <TableBody>
                  {this.state.detailsRows.map((row) => (
                    <TableRow
                      key={row.name}
                      sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                    >
                      <TableCell component="th" scope="row">
                        {row.name}
                      </TableCell>
                      <TableCell align="right">
                        {row.value}
                      </TableCell>
                    </TableRow>
                  ))}
                  <TableRow
                    sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                  >
                    <TableCell component="th" scope="row">
                      Actions
                    </TableCell>
                    <TableCell align="right">
                      <button mat-raised-button onClick={this.triggerRun} color="primary">Trigger Run</button>
                    </TableCell>
                  </TableRow>
                  {this.state.manualTriggerState !== null ? (
                    <TableRow
                      sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                    >
                      <TableCell component="th" scope="row">
                        Manual Trigger Status
                      </TableCell>
                      <TableCell align="right">
                        {this.state.manualTriggerState}
                      </TableCell>
                    </TableRow>
                  ) : (<div></div>)}
                </TableBody>
              </Table>
            </TableContainer>
          </Grid>

          <Grid
            item
            xs={12} md={12} lg={10} xl={8}
            sx={{
              '& .check-result-row--success': {
                bgcolor: '#ccffcc'
              },
              '& .check-result-row--failed': {
                bgcolor: '#ffcccc'
              }
            }}
          >
            <DateTimePicker
              label="From date"
              value={this.state.fromDate}
              onChange={this.setFromDate}
              />
            <DateTimePicker
              label="To date"
              value={this.state.toDate}
              onChange={this.setToDate}
              />
            <br />

            <div style={{ height: 800, width: '100%' }}>

              <Chart
                options={{
                  dataLabels: {
                    enabled: true
                  },
                  plotOptions: {
                    heatmap: {
                      colorScale: {
                        ranges: [
                          {
                            from: -1,
                            to: -1,
                            color: '#eeeeee',
                            name: 'No runs',
                          },
                          {
                            from: 0,
                            to: 90,
                            color: '#DC143C',
                          },
                          {
                            from: 90,
                            to: 99.0,
                            color: '#FF8C00',
                            name: 'medium',
                          },
                          {
                            from: 99.0,
                            to: 99.999,
                            color: '#FFD700',
                            name: 'high',
                          },
                          ,
                          {
                            from: 99.999,
                            to: 100.0,
                            color: '#ccffcc',
                            name: 'high',
                          },
                        ]
                      }
                    }
                  }
                }}
                series={this.state.heatmapData}
                type="heatmap"
                width="100%"
                height="150"
              />

              <DataGrid
                rows={this.state.runs}
                columns={columns}
                pageSize={100}
                rowsPerPageOptions={[5]}
                getRowId={(row: any) =>  row.timestamp}
                onRowClick={this.onRowClick}
                initialState={{
                  sorting: {
                    sortModel: [{ field: 'timestamp', sort: 'desc' }],
                  },
                }}
                getRowClassName={(params) => `check-result-row--${params.row.result === "SUCCESS" ? 'success' : (['FAILED', 'TIMEOUT', 'INTERNAL_ERROR'].indexOf(params.row.result) !== -1) ? 'failed' : 'running'}`}
              />
            </div>
          </Grid>
        </Grid>
      </Container>
    );
  }
}

export default withRouter(CheckView);
