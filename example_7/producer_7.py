import json
from example_7 import producer_count, message_count_per_producer

from common.traceable_logger import TraceableLogger
from common.ace_rabbitmq import RabbitmqService
import multiprocessing

logger = TraceableLogger(__name__)
exchange = 'tasks'
routing_key = 'tasks'

__all__ = {'publish_messages'}
queue = 'tasks'
QoS = 700
rmq = RabbitmqService(uri='amqp://guest:guest@192.168.99.100/',
                      exchange=exchange,
                      queue=queue,
                      routing_key=routing_key,
                      qos=QoS)


def publish():
    i = 0
    while i < message_count_per_producer:
        rmq.publish_fast(routing_key=routing_key,
                         message=json.dumps({'value': i}))
        i += 1


def publish_messages():
    global rmq
    if rmq.connection.is_closed:
        rmq = RabbitmqService(uri='amqp://guest:guest@192.168.99.100/',
                              exchange=exchange,
                              queue=queue,
                              routing_key=routing_key,
                              qos=QoS)

    n = producer_count * message_count_per_producer
    logger.info('Publish {} messages.'.format(n))

    prod_ths = []
    for _ in range(producer_count):
        prod_ths.append(multiprocessing.Process(target=publish))
    for prod_th in prod_ths:
        prod_th.start()
    for prod_th in prod_ths:
        prod_th.join()

    rmq.publish_fast(routing_key=routing_key,
                     message=json.dumps({'value': 'end'}))


if __name__ == '__main__':
    # Benchmark
    # import timeit
    # repeat = 3
    # number = 5
    # results = timeit.repeat(publish_messages, repeat=repeat, number=number)
    # print("Results: {}".format(results))
    # print("average: {}".format(sum(results)/repeat/number))
    # end benchmark

    publish_messages()
