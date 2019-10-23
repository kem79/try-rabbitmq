import json
import sys

from common.ace_rabbitmq import RabbitmqService
from common.traceable_logger import TraceableLogger
from example_2 import producer_count, message_count_per_producer

logger = TraceableLogger(__name__)
exchange = 'tasks'
routing_key = 'tasks'
queue = 'tasks'



if __name__ == '__main__':
    """
    This consumer only counts the received messages. it then asserts that the number of message is equal
    to the number of messages sent by the producer(s)
    """
    rmq = RabbitmqService(uri='amqp://guest:guest@192.168.99.100/')

    received_values = []

    def callback(channel, method, properties, body):
        val = json.loads(body.decode('utf-8'))['value']
        if val == 'end':
            raise SystemExit()
        received_values.append(val)

    while True:
        i = 0
        try:
            rmq.consume(callback=callback,
                        exchange=exchange,
                        queue=queue,
                        routing_key=routing_key
                        )
            i += 1
            print('{}\r'.format(i))
        except SystemExit:
            print('Interrupt')
            expected_count_of_received_messages = producer_count * message_count_per_producer
            assert len(received_values) >= expected_count_of_received_messages, \
                'Received {} messages. Not {}.'.format(len(received_values), expected_count_of_received_messages)
            sys.exit(0)


