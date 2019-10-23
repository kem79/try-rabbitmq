from time import sleep
import json
import threading
from threading import Lock
from common.ace_rabbitmq import RabbitmqService
from example_2 import producer_count, message_count_per_producer

exchange = 'tasks'
routing_key = 'tasks'
rmq = RabbitmqService(uri='amqp://guest:guest@192.168.99.100/', exchange=exchange)


def publish(mbarrier):
    i = 0
    try:
        while i < message_count_per_producer:
            rmq.publish3(exchange=exchange,
                         routing_key=routing_key,
                         message=json.dumps({'value': i}))
            i += 1
    finally:
        mbarrier.wait()


def feed_dead_pill():
    rmq.publish3(exchange=exchange,
                 routing_key=routing_key,
                 message=json.dumps({'value': 'end'}))
    print('Death pill...')


if __name__ == '__main__':
    barrier = threading.Barrier(producer_count, action=feed_dead_pill)
    producer_threads = []
    for producer_id in range(producer_count):
        producer_threads.append(threading.Thread(target=publish, args=(barrier,)))

    for producer_thread in producer_threads:
        producer_thread.start()
    for producer_thread in producer_threads:
        producer_thread.join()
    print('ending...')
