"""
This module is a copy of rabbitmq.py module that you can find in railai-common.
this copy is used to test and benchmark the our own code.
the goal is to verify reliability: do we loose message when advert events happen?
"""
import pika
from pika import exceptions
from retry import retry
from common.traceable_logger import TraceableLogger, get_trace_id, with_trace_id

logger = TraceableLogger(__name__)

CONNECTION_ERR_MSG = "AMQPError occurs, retry connection with exchange={}"
EXCHANGE_QUEUE_ERR_MSG = "exchange is None, please set env variables and restart service"


class RabbitmqService(object):
    '''
    When AMQPError occurs during publish/consume, it will retry with predefined times
    Both queue and message are durable
    '''
    # initial delay between attempts
    delay = 2
    # max delay
    max_delay = 10
    # extra seconds added to delay between attempts.
    jitter = (1, 3)
    # max retries
    retries = 3

    def __init__(self, uri, exchange=None):
        self.uri = uri
        self.connection = pika.BlockingConnection(pika.URLParameters(self.uri))
        self.channel = self.connection.channel()
        self.exchange = exchange
        if exchange:
            self.channel.exchange_declare(exchange=exchange, durable=True)


    '''
    Consume will retry infinitely if connection failed. Use tries default value -1.
    '''
    @retry(exceptions=pika.exceptions.AMQPError, max_delay=max_delay, delay=delay, jitter=jitter)
    def consume(self, callback, exchange, queue, routing_key):
        try:
            if exchange is None or queue is None:
                logger.error(EXCHANGE_QUEUE_ERR_MSG)
                return
            logger.info("Building consume connection exchange={}, queue={}".format(exchange, queue))
            connection = pika.BlockingConnection(pika.URLParameters(self.uri))
            channel = connection.channel()
            channel.exchange_declare(exchange=exchange, durable=True)
            channel.queue_declare(queue, durable=True)
            channel.queue_bind(exchange=exchange,
                               routing_key=routing_key,
                               queue=queue)
            channel.basic_consume(callback, queue=queue, no_ack=True)
            logger.info("Start consuming")
            channel.start_consuming()
        except pika.exceptions.AMQPError:
            logger.exception(CONNECTION_ERR_MSG.format(exchange))
            # Trigger retry
            raise

    '''
    Publish will retry #retries# times if connection failed
    '''
    @retry(exceptions=pika.exceptions.AMQPError, max_delay=max_delay, delay=delay, jitter=jitter)
    @with_trace_id
    def publish(self, exchange, routing_key, message, app_id=None, expiration=None):
        """
        This is the original method that you can find in railai-common package.
        :param exchange:
        :param routing_key:
        :param message:
        :param app_id:
        :param expiration:
        :return:
        """
        try:
            if exchange is None:
                logger.error(EXCHANGE_QUEUE_ERR_MSG)
                return
            logger.debug("Building publish connection exchange={}".format(exchange))
            connection = pika.BlockingConnection(pika.URLParameters(self.uri))
            # enable publisher confirm
            # channel.confirm_delivery()
            trace_id = get_trace_id()

            channel = connection.channel()
            channel.exchange_declare(exchange=exchange, durable=True)
            logger.info("publishing..." + message)
            channel.basic_publish(exchange=exchange,
                                  routing_key=routing_key,
                                  body=message,
                                  properties=pika.BasicProperties(delivery_mode=2,
                                                                  app_id=app_id,
                                                                  expiration=expiration,
                                                                  headers={'x-trace-id': trace_id}))
            connection.close()
            logger.debug("Finish publishing..." + message)
        except pika.exceptions.AMQPError:
            logger.exception(CONNECTION_ERR_MSG.format(exchange))
            # Trigger retry
            raise

    @retry(exceptions=pika.exceptions.AMQPError, tries=retries, max_delay=max_delay, delay=delay, jitter=jitter)
    @with_trace_id
    def publish2(self, routing_key, message, app_id=None, expiration=None):
        """
        this method is similar to publish(), except it does not create the connection nor the channel. They are
        created in the init method.
        :param routing_key:
        :param message:
        :param app_id:
        :param expiration:
        :return:
        """
        try:
            if self.exchange is None:
                logger.error(EXCHANGE_QUEUE_ERR_MSG)
                return
            logger.debug("Building publish connection exchange={}".format(self.exchange))
            # enable publisher confirm
            # channel.confirm_delivery()
            trace_id = get_trace_id()

            logger.info("publishing..." + message)
            self.channel.basic_publish(exchange=self.exchange,
                                       routing_key=routing_key,
                                       body=message,
                                       properties=pika.BasicProperties(delivery_mode=2,
                                                                       app_id=app_id,
                                                                       expiration=expiration,
                                                                       headers={'x-trace-id': trace_id}))
            logger.debug("Finish publishing..." + message)
        except pika.exceptions.AMQPError:
            logger.exception(CONNECTION_ERR_MSG.format(self.exchange))
            # Trigger retry
            raise

    @retry(exceptions=pika.exceptions.AMQPError, max_delay=max_delay, delay=delay, jitter=jitter)
    @with_trace_id
    def publish3(self, exchange, routing_key, message, app_id=None, expiration=None):
        """
        This is the original method that you can find in railai-common package.
        :param exchange:
        :param routing_key:
        :param message:
        :param app_id:
        :param expiration:
        :return:
        """
        try:
            if exchange is None:
                logger.error(EXCHANGE_QUEUE_ERR_MSG)
                return
            logger.debug("Building publish connection exchange={}".format(exchange))
            connection = pika.BlockingConnection(pika.URLParameters(self.uri))
            trace_id = get_trace_id()

            channel = connection.channel()
            # channel.confirm_delivery()
            channel.exchange_declare(exchange=exchange, durable=True)
            logger.info("publishing..." + message)
            channel.basic_publish(exchange=exchange,
                                  routing_key=routing_key,
                                  body=message,
                                  properties=pika.BasicProperties(delivery_mode=2,
                                                                  app_id=app_id,
                                                                  expiration=expiration,
                                                                  headers={'x-trace-id': trace_id}))
            connection.close()
            logger.debug("Finish publishing..." + message)
        except pika.exceptions.AMQPError:
            logger.exception(CONNECTION_ERR_MSG.format(exchange))
            # Trigger retry
            raise