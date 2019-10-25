
import json
from example_4 import producer_count, message_count_per_producer

from common.ace_rabbitmq import RabbitmqService

exchange = 'tasks'
routing_key = 'tasks'

if __name__ == '__main__':
    rmq = RabbitmqService(uri='amqp://guest:guest@192.168.99.100/', exchange=exchange)

    i = 0
    n = producer_count * message_count_per_producer
    while i < n:
        rmq.publish_fast(routing_key=routing_key,
                         message=json.dumps({'value': i}))
        i += 1
    rmq.publish_fast(routing_key=routing_key,
                     message=json.dumps({'value': 'end'}))
