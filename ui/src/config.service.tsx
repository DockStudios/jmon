import client from './client.tsx';


class ConfigService {

  getConfig() {
    return client.get(`/config`);
  }
}

export default ConfigService;
