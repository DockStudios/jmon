import { Dayjs } from 'dayjs';
import client from './client.tsx';

class CheckService {
  getAll() {
    return client.get("/checks");
  }

  getByNameAndEnvironment(name, environment) {
    return client.get(`/checks/${name}/environments/${environment}`);
  }

  getResultsByCheckNameAndEnvironment(name, environment, timeframe) {
    let args = '';
    if (timeframe) {
      args = `timeframe=${timeframe}`;
    }
    return client.get(`/checks/${name}/environments/${environment}/results?${args}`);
  }

  getHeatmapData(name: string, environment: string, fromDate: Dayjs, toDate: Dayjs) {
    return client.get(`/checks/${name}/environments/${environment}/heatmap-data`, {
      params: {
        from_date: fromDate.toISOString(),
        to_date: toDate.toISOString()
      }
    });
  }
}

export default CheckService;
