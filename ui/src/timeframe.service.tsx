import client from './client.tsx';


class TimeframeService {

  getTimeframes() {
    return client.get(`/result-timeframes`);
  }
}

export default TimeframeService;
