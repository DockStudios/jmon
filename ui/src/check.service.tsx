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
}

export default CheckService;
