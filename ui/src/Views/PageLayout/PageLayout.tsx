
import * as React from 'react';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { AppBar, Box, CssBaseline, Toolbar, Typography, Alert, Drawer, List, ListItem, ListItemButton, ListItemIcon, Divider, ListItemText } from '@mui/material';
import InboxIcon from '@mui/icons-material/MoveToInbox';
import { Outlet } from 'react-router-dom';
import QueueService from '../../queue.service.tsx';
import { withRouter } from '../../withRouter';

class PageLayout extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      open: true,
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
    this.onOverviewButtonClick = this.onOverviewButtonClick.bind(this);
    this.onInternalStatusButtonClick = this.onInternalStatusButtonClick.bind(this);
    this.mdTheme = createTheme();
  }

  toggleDrawer() {
    this.setState((state) => { return { ...state, open: !state.open }; });
  };

  componentDidMount() {
    this.getSystemAlerts();
  }

  getSystemAlerts() {
    new QueueService().getQueueStatus().then((queueStatusData) => {
      this.setState((state) => {
        return Object.assign({}, { ...state, queueStatus: queueStatusData.data });
      });
    });
  }

  onOverviewButtonClick() {
    this.props.navigate('/');
  }

  onInternalStatusButtonClick() {
    this.props.navigate('/status');
  }

  render() {

    const drawerWidth = 240;

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
            component="nav"
            sx={{ width: drawerWidth, flexShrink: 0 }}
            aria-label="navigation"
          >
            <Drawer
              variant="permanent"
              open
              ModalProps={{
                keepMounted: true, // Better open performance on mobile.
              }}
              sx={{
                display: 'block',
                '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
              }}
            >
              <Toolbar />
              <Divider />
              <List>
                <ListItem disablePadding>
                  <ListItemButton onClick={this.onOverviewButtonClick}>
                    <ListItemIcon>
                      <InboxIcon />
                    </ListItemIcon>
                    <ListItemText primary="Overview" />
                  </ListItemButton>
                </ListItem>

                <ListItem disablePadding>
                  <ListItemButton onClick={this.onInternalStatusButtonClick}>
                    <ListItemIcon>
                      <InboxIcon />
                    </ListItemIcon>
                    <ListItemText primary="Internal Status" />
                  </ListItemButton>
                </ListItem>
              </List>
            </Drawer>
          </Box>

          <Box
            component="main"
            sx={{
              backgroundColor: (theme) =>
                theme.palette.mode === 'light'
                  ? theme.palette.grey[100]
                  : theme.palette.grey[900],
              flexGrow: 1,
              p: 3,
              height: '100vh',
              overflow: 'auto',
              width: `calc(100% - ${drawerWidth}px)`
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

export default withRouter(PageLayout);
