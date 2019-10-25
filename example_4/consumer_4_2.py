import json
import sys
from time import sleep

from common.ace_rabbitmq import RabbitmqService
from common.traceable_logger import TraceableLogger
from example_4 import producer_count, message_count_per_producer

logger = TraceableLogger(__name__)
exchange = 'tasks'
routing_key = 'tasks'
queue = 'tasks'

if __name__ == '__main__':
    """
    This consumer only counts the received messages. it then asserts that the number of message is equal
    to the number of messages sent by the producer(s)
    """
    rmq = RabbitmqService(uri='amqp://guest:guest@192.168.99.100/',
                          exchange=exchange,
                          queue=queue,
                          routing_key=routing_key)

    received_values = []

    def callback(channel, method_frame, header_frame, body):
        val = json.loads(body.decode('utf-8'))['value']
        logger.info('Value: {} ; Delivery tag: {}'.format(val,
                                                          method_frame.delivery_tag))
        channel.basic_ack(method_frame.delivery_tag)
        if val == 'end':
            raise SystemExit()
        received_values.append(val)
        sleep(0.250)

    while True:
        i = 0
        try:
            rmq.consume_with_ack(callback=callback)
            i += 1
        except SystemExit:
            # assert the count of received messages
            print('Interrupt')
            expected_count_of_received_messages = producer_count * message_count_per_producer
            if len(received_values) != expected_count_of_received_messages:
                logger.error(
                    'Received {} messages. Not {}.'.format(len(received_values), expected_count_of_received_messages))
            else:
                logger.info('Received {} messages'.format(len(received_values)))
            sys.exit(0)


