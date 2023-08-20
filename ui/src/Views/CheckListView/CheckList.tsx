
import Container from '@mui/material/Container';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import TextField from '@mui/material/TextField';
import { DataGrid, GridColDef, GridCellParams, GridFilterModel, GridToolbar } from '@mui/x-data-grid';
import * as React from 'react';
import  { useState } from 'react';
import checkService from '../../check.service.tsx';
import ConfigService from '../../config.service.tsx';
import TimeframeService from '../../timeframe.service.tsx';
import { withRouter } from '../../withRouter';


class CheckList extends React.Component {

  columns: GridColDef[] = [];
  config = {
    check: {
      thresholds: {
        critical: null,
        warning: null
      }
    }
  };
  queryOptions = undefined;
  setQueryOptions = undefined;
  changeDebounceTimeout = undefined;

  constructor(props) {
    super(props);
    this.state = {
      checks: [],
      selectedTimeframe: 0,
      timeframes: [],
      filterQuery: ''
    };
    this.retrieveChecks = this.retrieveChecks.bind(this);
    this.onRowClick = this.onRowClick.bind(this);
    this.handleTimeframeChange = this.handleTimeframeChange.bind(this);
    this.onFilterChange = this.onFilterChange.bind(this);
    this.scheduleRetrieveChecks = this.scheduleRetrieveChecks.bind(this);
    this.retrieveChecksTimeoutHandle = this.retrieveChecksTimeoutHandle.bind(this);
  }

  onFilterChange(ev) {
    if (ev?.target) {
      this.setState((state) => Object.assign({}, {...state, filterText: ev?.target?.value}))
    }
    this.scheduleRetrieveChecks();
  }

  scheduleRetrieveChecks() {
    // On search change, cancel any pre-existing debounce timeout
    if (this.changeDebounceTimeout) {
      clearTimeout(this.changeDebounceTimeout);
    }

    // Create new timeout
    this.changeDebounceTimeout = setTimeout(this.retrieveChecksTimeoutHandle, 500);
  }
  retrieveChecksTimeoutHandle() {
    // Clear current debounce timeout and trigger retrieve checks
    this.changeDebounceTimeout = null;
    this.retrieveChecks();
  }

  async componentDidMount() {
    document.title = `JMon`;

    // Obtain config
    await new ConfigService().getConfig().then((config) => {
      this.config = config.data;
    });
    // Obtain timeframes for limiting data
    new TimeframeService().getTimeframes().then((data) => {
      this.setState((state) => Object.assign({}, {...state, timeframes: data.data}));
    })

    this.columns = [
      { field: 'environment', headerName: 'Environment', width: 200 },
      { field: 'name', headerName: 'Name', width: 400 },
      {
        field: 'average_success',
        headerName: 'Average Success',
        valueGetter: (data) => {return (data.row.average_success === null ? 'No runs' : (data.row.average_success >= 0.9999 ? '100' : (data.row.average_success * 100).toPrecision(4)) + '%');},
        width: 100
      },
      { field: 'latest_status', headerName: 'Latest Status', valueGetter: (data) => {return data.row.latest_status === true ? 'Success' : data.row.latest_status === false ? 'Failed' : 'Not run'} },
      { field: 'enable', headerName: 'Enabled', valueGetter: (data) => {return data.row.enable ? 'Enabled' : 'Disabled' } },
    ];

    // Obtain check rows for table
    this.retrieveChecks();
  }

  retrieveChecks() {
    const checkServiceIns = new checkService();
    checkServiceIns.getAll(
      // pageSize, page, searchFilter
    ).then((checksRes) => {
      let promises = checksRes.data.map((check) => {
        return new Promise((resolve, reject) => {
          checkServiceIns.getResultsByCheckNameAndEnvironment(check.name, check.environment, this.state.selectedTimeframe).then((statusRes) => {
            resolve({
              name: check.name,
              enable: check.enable,
              environment: check.environment,
              average_success: statusRes.data.average_success,
              latest_status: statusRes.data.latest_status
            });
          });
        });
      });
      Promise.all(promises).then((checkData) => {
        this.setState((state) => Object.assign({}, {...state, checks: checkData}));
      });
    });
  }

  onRowClick(val: any) {
    this.props.navigate(`/checks/${val.row.name}/environments/${val.row.environment}`);
  }

  handleTimeframeChange(ev: any) {
    if (ev?.target?.value !== undefined) {
      this.setState((state) => Object.assign({}, {...state, selectedTimeframe: ev.target.value}))
    }
    this.retrieveChecks();
  }

  render() {
    return (
      <Container  maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Grid container spacing={3}>

          <Grid item xs={12} md={3} lg={2} xl={2}>
            <FormControl fullWidth>
              <InputLabel id="timeframe-label">Timeframe</InputLabel>
              <Select
                labelId="timeframe-label"
                value={this.state.selectedTimeframe}
                label="Timeframe"
                onChange={this.handleTimeframeChange}
              >
                <MenuItem value={0}>All Time</MenuItem>
                {this.state.timeframes.map((timeframe) =>
                  <MenuItem key={timeframe.name} value={timeframe.name}>
                    {timeframe.friendly_name}
                  </MenuItem>
                )}
              </Select>
            </FormControl>
            <br />

            <FormControl fullWidth>
              <TextField onChange={this.onFilterChange} label="Filter" type="search" />
            </FormControl>
          </Grid>


          <Grid item xs={12} md={12} lg={10} xl={8} sx={{
                '& .check-row--disabled': {
                  bgcolor: '#eeeeee'
                },
                '& .check--ok': {
                  bgcolor: '#ccffcc'
                },
                '& .check--warning': {
                  bgcolor: '#fff1e1'
                },
                '& .check--critical': {
                  bgcolor: '#ffcccc'
                },
              }}
          >
            <div style={{ height: 500, width: '100%' }}>
              <DataGrid
                rows={this.state.checks}
                columns={this.columns}
                getRowId={(row: any) =>  row.name + row.environment}
                onRowClick={this.onRowClick}
                disableColumnFilter
                disableColumnSelector
                disableDensitySelector
                getRowClassName={(row) => {
                  if (!row.row.enable) {
                    return 'check-row--disabled';
                  }
                  return '';
                }}
                getCellClassName={(params: GridCellParams) => {
                  if (params.field == 'average_success') {
                    if (params.row.average_success * 100 <= this.config.check.thresholds.critical) {
                      return 'check--critical';
                    } else if (params.row.average_success * 100 <= this.config.check.thresholds.warning) {
                      return 'check--warning';
                    } else {
                      return 'check--ok';
                    }
                  } else if (params.field == 'latest_status') {
                    if (params.row.latest_status == true) {
                      return 'check--ok';
                    } else {
                      return 'check--critical';
                    }
                  }
                }}
              />
            </div>
          </Grid>
        </Grid>
      </Container>
    );
  }
}

export default withRouter(CheckList);
