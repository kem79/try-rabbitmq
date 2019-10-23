"""
A small module to time the produce method when the method does not create the connection.
"""
import timeit
import json
import os
import logging

from common.ace_rabbitmq import RabbitmqService

exchange = 'tasks'
routing_key = 'tasks'

rmq = RabbitmqService(uri='amqp://guest:guest@192.168.99.100/', exchange=exchange)
logging.disable(level=logging.CRITICAL)


def produce():
    rmq.publish2(
        routing_key=routing_key,
        message=json.dumps({'value': '1'}))


if __name__ == '__main__':
    print('Start...')
    # experiment 10000 calls to produce, 10 times
    res = timeit.repeat(produce, repeat=3, number=100)
    print('runs: {}'.format(res))
    print('average: {}'.format(sum(res) / 3))
