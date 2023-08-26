import client from './client.tsx';


class QueueService {

  getQueueStatus() {
    return client.get(`/status/queues`);
  }
}

export default QueueService;
