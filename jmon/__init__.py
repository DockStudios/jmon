
import os

from celery import Celery, bootsteps
from kombu import Queue, Exchange, binding
from redbeat.schedulers import RedBeatConfig

from jmon.logger import logger
import jmon.config

redis_url = f"{os.environ.get('REDIS_TYPE')}://{os.environ.get('REDIS_USERNAME')}:{os.environ.get('REDIS_PASSWORD')}@{os.environ.get('REDIS_HOST')}:{os.environ.get('REDIS_PORT')}/{os.environ.get('REDIS_INSTANCE')}"
broker_url = f"{os.environ.get('BROKER_TYPE')}://{os.environ.get('BROKER_USERNAME')}:{os.environ.get('BROKER_PASSWORD')}@{os.environ.get('BROKER_HOST')}:{os.environ.get('BROKER_PORT')}/{os.environ.get('BROKER_INSTANCE')}"

app = Celery(
    "server",
    backend=redis_url,
    broker=broker_url
)

app.conf.task_default_queue = 'default'
app.conf.result_expires = jmon.config.Config.get().QUEUE_TASK_RESULT_RETENTION_MINS

task_exchange = Exchange('task', type='direct')
check_exchange = Exchange('check', type='headers')

# Task deadletter exchange and queue
dead_letter_queue_name = "task-dlq"
dead_letter_exchange_name = "task-dlq-ex"
dead_letter_routing_key = "task-dlq"

dead_letter_exchange = Exchange(dead_letter_exchange_name, type='direct')

dead_letter_queue = Queue(
    dead_letter_queue_name, dead_letter_exchange, routing_key=dead_letter_routing_key
)

class AdditionalExchangeQueueCreation(bootsteps.StartStopStep):
    """
    Handle the creation of additional queues/exchanges
    """
    requires = {'celery.worker.components:Pool'}

    def start(self, worker):
        """On start, create deadletter queue and exchange"""
        # Declare deadletter queues
        with worker.app.pool.acquire() as conn:
            dead_letter_queue.bind(conn).declare()


app.conf.task_queues = (
    Queue('default', exchange=task_exchange, routing_key='task.default'),
    Queue(
        'requests',
        bindings=[
            binding(exchange=check_exchange, arguments={'x-match': 'any', 'requests': 'true'})
        ],
        queue_arguments={
            'x-dead-letter-exchange': dead_letter_exchange_name,
            'x-dead-letter-routing-key': dead_letter_routing_key
        }
    ),
    Queue(
        'firefox',
        bindings=[
            binding(exchange=check_exchange, arguments={'x-match': 'any', 'firefox': 'true'})
        ],
        queue_arguments={
            'x-dead-letter-exchange': dead_letter_exchange_name,
            'x-dead-letter-routing-key': dead_letter_routing_key
        }
    ),
    Queue(
        'chrome',
        exchange=check_exchange,
        bindings=[
            binding(exchange=check_exchange, arguments={'x-match': 'any', 'chrome': 'true'})
        ],
        queue_arguments={
            'x-dead-letter-exchange': dead_letter_exchange_name,
            'x-dead-letter-routing-key': dead_letter_routing_key
        }
    )
)

app.steps['worker'].add(AdditionalExchangeQueueCreation)
app.conf.task_default_exchange = task_exchange.name
app.conf.task_default_exchange_type = task_exchange.type
app.conf.task_default_routing_key = 'task.default'

# Setup default redbeat config
app.conf.redbeat_redis_url = redis_url
app.redbeat_conf = RedBeatConfig(app=app)

logger.info("Imported jmon")
