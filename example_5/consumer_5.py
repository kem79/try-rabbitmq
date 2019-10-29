import json
import sys
from time import sleep

from common.ace_rabbitmq import RabbitmqService
from common.traceable_logger import TraceableLogger
from example_5 import producer_count, message_count_per_producer, rmq, QoS

logger = TraceableLogger(__name__)
exchange = 'tasks'
routing_key = 'tasks'
queue = 'tasks'
# QoS = 100
#
# rmq = RabbitmqService(uri='amqp://guest:guest@192.168.99.100/',
#                       exchange=exchange,
#                       queue=queue,
#                       routing_key=routing_key)
# To store received messages
received_values = []


def callback(channel, method_frame, header_frame, body):
    val = json.loads(body.decode('utf-8'))['value']
    channel.basic_ack(method_frame.delivery_tag)
    if val == 'end':
        raise SystemExit()
    received_values.append(val)


def consume():
    """
    This consumer only counts the received messages. it then asserts that the number of message is equal
    to the number of messages sent by the producer(s).
    The channel QoS is specified.
    """
    global received_values
    received_values = []
    while True:
        i = 0
        try:
            rmq.consume(callback=callback, exchange=exchange, queue=queue, routing_key=routing_key, prefetch_count=QoS)
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
            break
    return


if __name__ == '__main__':
    import timeit
    from producer_5 import produce
    print("purge messages")
    rmq.channel.queue_purge('tasks')
    print('Start...')
    # repeat the produce/consume experiment several times
    repeat = 3
    res = timeit.repeat(consume, produce, repeat=repeat, number=1)
    print('runs: {}'.format(res))
    print('average run: {}'.format(sum(res)/repeat))




