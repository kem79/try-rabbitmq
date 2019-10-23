"""
A small module to time the produce method when the method create the connection.
"""
import timeit
import json
import logging

from common.ace_rabbitmq import RabbitmqService
logging.disable(level=logging.CRITICAL)

exchange = 'tasks'
routing_key = 'tasks'

rmq = RabbitmqService(uri='amqp://guest:guest@192.168.99.100/')

def produce():
    """
    each call to publish create a connection
    :return:
    """
    rmq.publish(exchange=exchange,
                routing_key=routing_key,
                message=json.dumps({'value': '1'}))


if __name__ == '__main__':
    print('Start...')
    # experiment 100 calls to produce, 3 times
    res = timeit.repeat(produce, repeat=3, number=100)
    print('runs: {}'.format(res))
    print('average: {}'.format(sum(res)/3))

