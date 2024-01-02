import { Dayjs } from 'dayjs';
import client from './client.tsx';


class CheckService {

  listByCheck(name: string, environment: string, fromDate: Dayjs, toDate: Dayjs) {
    return client.get(`/checks/${name}/environments/${environment}/runs`, {
      params: {
        from_date: fromDate.toISOString(),
        to_date: toDate.toISOString()
      }
    });
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
