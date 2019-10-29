import json
import threading
from queue import Queue

import pika
import sys

from common.traceable_logger import TraceableLogger
from example_5 import producer_count, message_count_per_producer, rmq
from example_6.producer_6 import produce

logger = TraceableLogger(__name__)

lock = threading.Lock()
lock2 = threading.Lock()
message_count = 0

death_pill_count = 0
# exception queue
exception_queue = Queue()




def increment_death_pill_count():
    global death_pill_count
    with lock:
        death_pill_count += 1

def get_death_pill_count():
    global death_pill_count
    with lock:
        return death_pill_count

def increment():
    global message_count
    with lock2:
        message_count += 1

def get_message_count():
    global message_count
    with lock2:
        return message_count

def check_result():
    expected_count_of_received_messages = producer_count * message_count_per_producer
    if message_count != expected_count_of_received_messages:
        logger.error(
            'Received {} messages. Not {}.'.format(message_count, expected_count_of_received_messages))

    else:
        logger.info('Received {} messages'.format(message_count))
    sys.exit(0)


barrier = threading.Barrier(parties=2, action=check_result)


def callback(channel, method_frame, header_frame, body):
    val = json.loads(body.decode('utf-8'))['value']
    channel.basic_ack(method_frame.delivery_tag)
    if val == 'end':
        print('end')
        channel.close(reply_code=0)
        barrier.wait()
    else:
        increment()


def consume(channel, queue):
    """
    This consumer only counts the received messages. it then asserts that the number of message is equal
    to the number of messages sent by the producer(s).
    """
    print('consume')
    channel.basic_consume(consumer_callback=callback, queue=queue)
    channel.start_consuming()


if __name__ == '__main__':
    QoS = 1

    connection = pika.BlockingConnection(pika.URLParameters('amqp://guest:guest@192.168.99.100/'))
    # purge messages in "tasks" queue
    ch = connection.channel()
    ch.queue_declare('tasks', durable=True)
    ch.exchange_declare('tasks', durable=True)
    ch.queue_purge(queue='tasks')
    ch.close()

    def test_consume():
        # 1st channel
        my_channel1 = connection.channel()
        my_channel1.basic_qos(prefetch_count=QoS, all_channels=False)
        my_channel1.queue_bind('tasks', 'tasks', 'tasks')

        # 2nd channel
        my_channel2 = connection.channel()
        my_channel2.basic_qos(prefetch_count=QoS, all_channels=False)
        my_channel2.queue_bind('tasks', 'tasks', 'tasks')


        consumer_ths = []
        consumer1_th = threading.Thread(target=consume, args=(my_channel1, 'tasks',))
        consumer_ths.append(consumer1_th)
        consumer2_th = threading.Thread(target=consume, args=(my_channel2, 'tasks',))
        consumer_ths.append(consumer2_th)

        for th in consumer_ths:
            th.start()
        for th in consumer_ths:
            th.join()



    import timeit
    repeat = 2
    result = timeit.repeat(test_consume, setup=produce, repeat=repeat, number=1)
    logger.info('Results: {}'.format(result))





