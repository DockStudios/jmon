
import { Typography } from '@mui/material';
import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import RunConfigGraph from '../../components/RunConfigGraph/RunConfigGraph.tsx';
import * as React from 'react';
import client from '../../client.tsx';
import runService from '../../run.service.tsx';
import { withRouter } from '../../withRouter';


class RunView extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      run: {artifacts: [], status: undefined},
      log: "",
      graphData: []
    };
    this.retrieveRun = this.retrieveRun.bind(this);
    this.screenshotFromArtifact = this.screenshotFromArtifact.bind(this);
  }

  componentDidMount() {
    document.title = `JMon - ${this.props.match.checkName} - ${this.props.match.environmentName} - ${this.props.match.runTimestamp}`;
    this.retrieveRun();
  }

  retrieveRun() {
    new runService().getById(this.props.match.checkName, this.props.match.environmentName, this.props.match.runTimestamp).then((runRes) => {
      this.setState((state) => Object.assign({}, {
        ...state,
        run: runRes.data
      }));
    });
    new runService().getLogById(this.props.match.checkName, this.props.match.environmentName, this.props.match.runTimestamp).then((runRes) => {
      this.setState((state) => Object.assign({}, {
        ...state,
        log: runRes.data
      }));
    });

    new runService().getGraphDataById(this.props.match.checkName, this.props.match.environmentName, this.props.match.runTimestamp).then((graphDataRes) => {
      this.setState((state) => Object.assign({}, {...state, graphData: graphDataRes.data}));
    });
  }


  screenshotFromArtifact(artifactName) {
    if (artifactName.indexOf('.png', artifactName.length - 4) !== -1) {
      let imageUrl = (client.defaults.baseURL + "/checks/" +
        this.props.match.checkName +
        "/environments/" + this.props.match.environmentName +
        "/runs/" + this.props.match.runTimestamp + "/artifacts/" + artifactName);
      return (
        <Grid
          item
          key={artifactName}
          xs={12} md={8} lg={4} xl={4}
          sx={{
            '& .artifact-image': {
              borderColor: 'black',
              borderStyle: 'solid',
              borderWidth: '1px',

              maxHeight: '100%',
              maxWidth: '100%'
            },
            '& a': {
              color: 'inherit',
              textDecoration: 'inherit'
            }
          }}
        >
          <a href={imageUrl}>
            <span>{artifactName}</span>
            <img className='artifact-image' src={imageUrl} />
          </a>
        </Grid>
      );
    } else {
      return <div key={artifactName}></div>;
    }
  }

  render() {
    return (
      <Container  maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Typography component="h2" variant="h5">
          {this.props.match.checkName} - {this.props.match.environmentName} - {this.props.match.runTimestamp}
        </Typography>
        <Grid container spacing={3} sx={{textAlign: 'left'}}>
          <Grid
            item
            xs={12} md={12} lg={10} xl={8}
          >
            <RunConfigGraph graphData={this.state.graphData}></RunConfigGraph>

            <Typography component="h4" variant="h5">
              Log
            </Typography>
            <code>
              <pre>{this.state.log}</pre>
            </code>
          </Grid>

          <Grid
            item
            xs={12} md={12} lg={12} xl={12}
          >
            <Typography component="h4" variant="h5">
              Screenshots
            </Typography>
            <Grid
              item
              container
              spacing={4}
              xs={12} md={12} lg={12} xl={12}
            >
              {this.state.run.artifacts.map((val) => this.screenshotFromArtifact(val))}
            </Grid>
          </Grid>
        </Grid>
      </Container>
    );
  }
}

export default withRouter(RunView);
