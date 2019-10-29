
import json
from example_5 import producer_count, message_count_per_producer

from common.traceable_logger import TraceableLogger
# from example_6 import rmq
from common.ace_rabbitmq import RabbitmqService

logger = TraceableLogger(__name__)
exchange = 'tasks'
routing_key = 'tasks'

__all__ = {'produce'}
queue = 'tasks'
QoS = 700
rmq = RabbitmqService(uri='amqp://guest:guest@192.168.99.100/',
                      exchange=exchange,
                      queue=queue,
                      routing_key=routing_key,
                      qos=QoS)


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
    rmq.publish_fast(routing_key=routing_key,
                     message=json.dumps({'value': 'end'}))


if __name__ == '__main__':
    produce()
