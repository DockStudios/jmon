
import Container from '@mui/material/Container';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import { DataGrid, GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import * as React from 'react';
import checkService from '../../check.service.tsx';
import ConfigService from '../../config.service.tsx';
import { withRouter } from '../../withRouter';


class CheckList extends React.Component {

  columns: GridColDef[] = [];

  constructor(props) {
    super(props);
    this.state = {
      checks: []
    };
    this.retrieveChecks = this.retrieveChecks.bind(this);
    this.onRowClick = this.onRowClick.bind(this);
  }

  componentDidMount() {
    document.title = `JMon`;

    new ConfigService().getConfig().then((config) => {
      this.columns = [
        { field: 'environment', headerName: 'Environment', width: 200 },
        { field: 'name', headerName: 'Name', width: 400 },
        {
          field: 'average_success',
          headerName: 'Average Success',
          valueGetter: (data) => {return (data.row.average_success >= 0.9999 ? '100' : (data.row.average_success * 100).toPrecision(4)) + '%';},
          renderCell: (params: GridRenderCellParams) => {
            let color = '#ccffcc'
            if (params.row.average_success * 100 <= config.data.check.thresholds.critical) {
              color = '#ffcccc';
            } else if (params.row.average_success * 100 <= config.data.config.check.thresholds.warning) {
              color = '#fff1e1';
            }

            return (
              <Box
                sx={{
                  backgroundColor: color,
                  width: "100%",
                  height: "100%",
                  display: "flex",
                  alignItems: "center",
                }}
              >
                <div sx={{margin: "auto", position: "relative", textAlign: "center"}}>
                  {params.value}
                </div>
              </Box>
            );
          },
          with: 300
        },
        { field: 'latest_status', headerName: 'Latest Status', valueGetter: (data) => {return data.row.latest_status === true ? 'Success' : data.row.latest_status === false ? 'Failed' : 'Not run'} },
        { field: 'enable', headerName: 'Enabled', valueGetter: (data) => {return data.row.enable ? 'Enabled' : 'Disabled' } },
      ];
      this.retrieveChecks();
    });
  }

  retrieveChecks() {
    const checkServiceIns = new checkService();
    checkServiceIns.getAll().then((checksRes) => {
      let promises = checksRes.data.map((check) => {
        return new Promise((resolve, reject) => {
          checkServiceIns.getResultsByCheckNameAndEnvironment(check.name, check.environment).then((statusRes) => {
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
        this.setState({checks: checkData});
      });
    });
  }

  onRowClick(val: any) {
    this.props.navigate(`/checks/${val.row.name}/environments/${val.row.environment}`);
  }

  render() {
    return (
      <Container  maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={12} lg={10} xl={8} sx={{
                '& .check-row--disabled': {
                  bgcolor: '#eeeeee'
                },
              }}
            >
            <div style={{ height: 500, width: '100%' }}>
              <DataGrid
                rows={this.state.checks}
                columns={this.columns}
                getRowId={(row: any) =>  row.name + row.environment}
                onRowClick={this.onRowClick}
                getRowClassName={(row) => {
                  if (!row.row.enable) {
                    return 'check-row--disabled';
                  }
                  return '';
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
