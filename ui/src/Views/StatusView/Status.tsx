
import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import * as React from 'react';
import QueueService from '../../queue.service.tsx';
import { withRouter } from '../../withRouter';


const agentCountByQueueColumns: GridColDef[] = [
  { field: 'queue', headerName: 'Queue', width: 200 },
  { field: 'count', headerName: 'Agent Count', width: 400 },
];

class StatusView extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      agentCountByQueue: []
    };
    this.retrieveStatus = this.retrieveStatus.bind(this);
  }

  componentDidMount() {
    document.title = `JMon - Status`;
    this.retrieveStatus();
  }

  retrieveStatus() {
    const queueService = new QueueService();
    queueService.getQueueStatus().then((queueStatusRes) => {
      this.setState((state) => {
        return Object.assign({},
          {...state,
            agentCountByQueue: Object.keys(queueStatusRes.data.queue_agent_count).map((queueName) => {
              return {
                queue: queueName,
                count: queueStatusRes.data.queue_agent_count[queueName]
              };
            })
          }
        )});
    });
  }

  render() {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={12} lg={10} xl={8} sx={{
            '& .check-row--disabled': {
              bgcolor: '#eeeeee'
            }
          }}
          >
            <div style={{ height: 500, width: '100%' }}>
              <h2>Agent Count by Queue</h2>
              <DataGrid
                rows={this.state.agentCountByQueue}
                columns={agentCountByQueueColumns}
                getRowId={(row: any) => row.queue}
              />
            </div>
          </Grid>
        </Grid>
      </Container>
    );
  }
}

export default withRouter(StatusView);
