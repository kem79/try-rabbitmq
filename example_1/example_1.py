from time import sleep
import json

from common.ace_rabbitmq import RabbitmqService

exchange = 'tasks'
routing_key = 'tasks'

if __name__ == '__main__':
    rmq = RabbitmqService(uri='amqp://guest:guest@192.168.99.100/')

    i = 0
    while i < 100:
        rmq.publish(exchange=exchange,
                    routing_key=routing_key,
                    message=json.dumps({'value': i}))
        i += 1
        sleep(2)