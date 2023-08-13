
import * as React from 'react';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { AppBar, Box, CssBaseline, Toolbar, Typography, Alert } from '@mui/material';
import { Outlet } from 'react-router-dom';
import QueueService from '../../queue.service.tsx';

class PageLayout extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      open: false,
      queueStatus: {
        queue_agent_count: {
          default: null,
          firefox: null,
          chrome: null,
          requests: null
        }
      }
    };
    this.toggleDrawer = this.toggleDrawer.bind(this);
    this.mdTheme = createTheme();
  }

  toggleDrawer() {
    this.setState((state) => {return {...state, open: !state.open};});
  };

  componentDidMount() {
    this.getSystemAlerts();
  }

  getSystemAlerts() {
    new QueueService().getQueueStatus().then((queueStatusData) => {
      this.setState((state) => {
        return Object.assign({}, {...state, queueStatus: queueStatusData.data});
      });
    });
  }

  render() {
    return (
      <ThemeProvider theme={this.mdTheme}>
        <Box sx={{ display: 'flex' }}>

          <CssBaseline />
          <AppBar>
            <Toolbar
              sx={{
                pr: '48px', // keep right padding when drawer closed
              }}
            >
              <Typography
                component="h1"
                variant="h6"
                color="inherit"
                noWrap
                sx={{ flexGrow: 1 }}
              >
                JMon
              </Typography>
              <Typography
                color="inherit"
                noWrap
                sx={{ flexGrow: 1 }}
              >
                Made with &lt;3 - github.com/matthewjohn/jmon
              </Typography>
            </Toolbar>
          </AppBar>
          <Box
            component="main"
            sx={{
              backgroundColor: (theme) =>
                theme.palette.mode === 'light'
                  ? theme.palette.grey[100]
                  : theme.palette.grey[900],
              flexGrow: 1,
              height: '100vh',
              overflow: 'auto',
            }}
          >
            <Toolbar />

            {this.state.queueStatus.queue_agent_count?.default === 0 ? (
              <Alert severity="error">
                Error: There are no running agents processing the default queue
              </Alert>
            ) : (<div></div>)}
            <Outlet />

          </Box>
        </Box>
      </ThemeProvider>
    );
  }
}

export default PageLayout;
