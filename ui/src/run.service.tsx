import client from './client.tsx';


class CheckService {

  listByCheck(name, environment) {
    return client.get(`/checks/${name}/environments/${environment}/runs`);
  }

  getById(name, environment, runTimestamp) {
    return client.get(`/checks/${name}/environments/${environment}/runs/${runTimestamp}`);
  }

  getLogById(name, environment, runTimestamp) {
    return client.get(`/checks/${name}/environments/${environment}/runs/${runTimestamp}/artifacts/artifact.log`);
  }

  getGraphDataById(name, environment, runTimestamp) {
    return client.get(`/checks/${name}/environments/${environment}/runs/${runTimestamp}/step-graph-data`);
  }

  triggerRun(name, environment) {
    return client.post(`/checks/${name}/environments/${environment}/trigger`);
  }

  getManualTriggerStatus(name, environment, triggerId) {
    return client.get(`/checks/${name}/environments/${environment}/trigger/${triggerId}`);
  }
}

export default CheckService;
