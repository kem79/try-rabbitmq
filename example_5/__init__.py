producer_count = 1
message_count_per_producer = 2000

exchange = 'tasks'
routing_key = 'tasks'
queue = 'tasks'
QoS = 100

# specify QoS
from common.ace_rabbitmq import RabbitmqService
rmq = RabbitmqService(uri='amqp://guest:guest@192.168.99.100/',
                      exchange=exchange,
                      queue=queue,
                      routing_key=routing_key,
                      qos=QoS)