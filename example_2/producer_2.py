import json
import threading
from common.ace_rabbitmq import RabbitmqService
from example_2 import producer_count, message_count_per_producer

exchange = 'tasks'
routing_key = 'tasks'
rmq = RabbitmqService(uri='amqp://guest:guest@192.168.99.100/', exchange=exchange)


def publish(mbarrier):
    i = 0
    try:
        while i < message_count_per_producer:
            rmq.publish2(
                        routing_key=routing_key,
                        message=json.dumps({'value': i}))
            i += 1
    finally:
        # The thread waits at the barrier until all threads reach here.
        mbarrier.wait()


def feed_dead_pill():
    """
    this is the signal to the consumer to make it understand this is the end.
    :return:
    """
    rmq = RabbitmqService(uri='amqp://guest:guest@192.168.99.100/', exchange=exchange)
    rmq.publish2(
                  routing_key=routing_key,
                  message=json.dumps({'value': 'end'}))
    print('Death pill...')


if __name__ == '__main__':
    # the barrier synchronized all the threads after they all published their message
    # this is to ensure that that death pill that marks the end of the publishing cycle is the last
    # message sent to the queue.
    barrier = threading.Barrier(producer_count, action=feed_dead_pill)
    producer_threads = []
    for producer_id in range(producer_count):
        producer_threads.append(threading.Thread(target=publish, args=(barrier,)))

    for producer_thread in producer_threads:
        producer_thread.start()
    for producer_thread in producer_threads:
        producer_thread.join()
    print('ending...')
