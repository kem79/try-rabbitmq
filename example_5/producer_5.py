
import json
from example_5 import producer_count, message_count_per_producer

from common.ace_rabbitmq import RabbitmqService
from common.traceable_logger import TraceableLogger
from example_5 import rmq

logger = TraceableLogger(__name__)
exchange = 'tasks'
routing_key = 'tasks'
# rmq = RabbitmqService(uri='amqp://guest:guest@192.168.99.100/', exchange=exchange, qos=)

__all__ = {'produce'}


def produce():
    i = 0
    n = producer_count * message_count_per_producer
    logger.info('Publish {} messages.'.format(n))
    while i < n:
        rmq.publish_fast(routing_key=routing_key,
                         message=json.dumps({'value': i}))
        i += 1
    rmq.publish_fast(routing_key=routing_key,
                     message=json.dumps({'value': 'end'}))


if __name__ == '__main__':
    produce()
