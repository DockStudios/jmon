
import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import * as React from 'react';
import checkService from '../../check.service.tsx';
import { withRouter } from '../../withRouter';


const columns: GridColDef[] = [
  { field: 'environment', headerName: 'Environment', width: 200 },
  { field: 'name', headerName: 'Name', width: 400 },
  { field: 'average_success', headerName: 'Average Success', valueGetter: (data) => {return (data.row.average_success >= 0.99 ? '100' : (data.row.average_success * 100).toPrecision(2)) + '%';} },
  { field: 'latest_status', headerName: 'Latest Status', valueGetter: (data) => {return data.row.latest_status === true ? 'Success' : data.row.latest_status === false ? 'Failed' : 'Not run'} },
  { field: 'enable', headerName: 'Enabled', valueGetter: (data) => {return data.row.enable ? 'Enabled' : 'Disabled' } },
];

class CheckList extends React.Component {

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
    this.retrieveChecks();
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
                }
              }}
            >
            <div style={{ height: 500, width: '100%' }}>
              <DataGrid
                rows={this.state.checks}
                columns={columns}
                getRowId={(row: any) =>  row.name + row.environment}
                onRowClick={this.onRowClick}
                getRowClassName={(row) => {return row.row.enable ? '' : 'check-row--disabled'}}
              />
            </div>
          </Grid>
        </Grid>
      </Container>
    );
  }
}

export default withRouter(CheckList);
