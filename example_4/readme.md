# Consumer Reliability
In the past examples, we focused on producer reliability, let's now focus on consumer reliability.
The consume() method tested in the next examples is the same as the method of railai-common.

As usual, the purpose of the experiments is to understand how ACE custom rabbitmq consume() method behaves in 
particular scenario, and to answer the question: "Do we lose messages?".

# Experiment 1: Consumer reliability without message acknowledgement.
producer_4.py contains one producer which publish 20000 messages on one channel with delivery confirm enable.
the publish_fast() method have been striped of connection/channel management and of logging message to make it 
fast.

consumer_4.py contains one consumer. It uses the consume() method of the rabbitmq.py module like the method we use in
railai-common package. The consumer logs received message. It also asserts the count of messages received and
compares it with the count of messages sent by the producer to the broker. If no message is lost, these 2 numbers
should be identical.

consume() method enable "no_ack", which means that the broker does not expect any message acknowledgment from the 
consumer. if there is  handshake, there is no validation that messages are delivered successfully to the consumer. 

## Test Introduction.
First, We will store 20001 messages (20000 + death pill message) in the "tasks" queue using the producer.
Next, we will start the consumer. While the consumer is running, we will stop/start the broker to simulate one 
disconnection.
Finally, we will verify if the consumer consumed all the messages.


## Test Protocol.
1) Start you rabbitmq broker and purge the messages in the "tasks" queue.
2) In the init file, set the number of producer to 1 and the number of messages to 20000.
2) Run producer.py and you should witness that you have 20001 messages in the "task" queue.
3) Start the consumer_4.py. 
4) While the consumer runs, stop the broker. You will notice that the consumer keeps on running
as if nothing happened, consuming a few hundreds of messages, until it eventually throws a connection error.
5) Start the broker again. The consumer connects and log messages. Let the consumer run until it completes
6) The consumer returns an error messages: the number of received messages is lower then 20000.

Here is the trace of the test:
```
2019-10-25 10:35:30,623 [INFO] Building consume connection exchange=tasks, queue=tasks C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py 54 1ca8e94a-f6d0-11e9-a1ae-8c04ba69e459 default 28036
2019-10-25 10:35:30,677 [INFO] Start consuming C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py 70 1ca8e94a-f6d0-11e9-a1ae-8c04ba69e459 default 28036
2019-10-25 10:35:30,685 [INFO] Value: 0 ; Delivery tag: 1 C:/Users/marecm/PycharmProjects/try-ace-rabbitmq/example_4/consumer_4.py 26 1ca8e94a-f6d0-11e9-a1ae-8c04ba69e459 default 28036
2019-10-25 10:35:30,718 [INFO] Value: 1 ; Delivery tag: 2 C:/Users/marecm/PycharmProjects/try-ace-rabbitmq/example_4/consumer_4.py 26 1ca8e94a-f6d0-11e9-a1ae-8c04ba69e459 default 28036
...
2019-10-25 10:36:03,227 [INFO] Value: 995 ; Delivery tag: 996 C:/Users/marecm/PycharmProjects/try-ace-rabbitmq/example_4/consumer_4.py 26 1ca8e94a-f6d0-11e9-a1ae-8c04ba69e459 default 28036
2019-10-25 10:36:03,259 [INFO] Value: 996 ; Delivery tag: 997 C:/Users/marecm/PycharmProjects/try-ace-rabbitmq/example_4/consumer_4.py 26 1ca8e94a-f6d0-11e9-a1ae-8c04ba69e459 default 28036
2019-10-25 10:36:03,289 [ERROR] AMQPError occurs, retry connection with exchange=tasks C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py 73 1ca8e94a-f6d0-11e9-a1ae-8c04ba69e459 default 28036
Traceback (most recent call last):
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py", line 71, in consume
    channel.start_consuming()
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 1780, in start_consuming
    self.connection.process_data_events(time_limit=None)
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 707, in process_data_events
    self._flush_output(common_terminator)
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 474, in _flush_output
    result.reason_text)
pika.exceptions.ConnectionClosed: (-1, "ConnectionResetError(10054, 'An existing connection was forcibly closed by the remote host', None, 10054, None)")
2019-10-25 10:36:05,294 [INFO] Building consume connection exchange=tasks, queue=tasks C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py 54 1ca8e94a-f6d0-11e9-a1ae-8c04ba69e459 default 28036
2019-10-25 10:36:05,549 [ERROR] AMQPError occurs, retry connection with exchange=tasks C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py 73 1ca8e94a-f6d0-11e9-a1ae-8c04ba69e459 default 28036
Traceback (most recent call last):
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py", line 55, in consume
    connection = pika.BlockingConnection(pika.URLParameters(self.uri))
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 374, in __init__
    self._process_io_for_connection_setup()
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 414, in _process_io_for_connection_setup
    self._open_error_result.is_ready)
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 468, in _flush_output
    raise exceptions.ConnectionClosed(maybe_exception)
pika.exceptions.ConnectionClosed: Connection to 192.168.99.100:5672 failed: timeout
2019-10-25 10:36:10,009 [INFO] Building consume connection exchange=tasks, queue=tasks C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py 54 1ca8e94a-f6d0-11e9-a1ae-8c04ba69e459 default 28036
2019-10-25 10:36:10,266 [ERROR] AMQPError occurs, retry connection with exchange=tasks C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py 73 1ca8e94a-f6d0-11e9-a1ae-8c04ba69e459 default 28036
Traceback (most recent call last):
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py", line 55, in consume
    connection = pika.BlockingConnection(pika.URLParameters(self.uri))
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 374, in __init__
    self._process_io_for_connection_setup()
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 414, in _process_io_for_connection_setup
    self._open_error_result.is_ready)
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 468, in _flush_output
    raise exceptions.ConnectionClosed(maybe_exception)
pika.exceptions.ConnectionClosed: Connection to 192.168.99.100:5672 failed: timeout
2019-10-25 10:36:17,226 [INFO] Building consume connection exchange=tasks, queue=tasks C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py 54 1ca8e94a-f6d0-11e9-a1ae-8c04ba69e459 default 28036
2019-10-25 10:36:17,261 [INFO] Start consuming C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py 70 1ca8e94a-f6d0-11e9-a1ae-8c04ba69e459 default 28036
2019-10-25 10:36:17,266 [INFO] Value: 8900 ; Delivery tag: 1 C:/Users/marecm/PycharmProjects/try-ace-rabbitmq/example_4/consumer_4.py 26 1ca8e94a-f6d0-11e9-a1ae-8c04ba69e459 default 28036
2019-10-25 10:36:17,296 [INFO] Value: 8901 ; Delivery tag: 2 C:/Users/marecm/PycharmProjects/try-ace-rabbitmq/example_4/consumer_4.py 26 1ca8e94a-f6d0-11e9-a1ae-8c04ba69e459 default 28036
...
2019-10-25 10:37:44,153 [INFO] Value: 19998 ; Delivery tag: 1399 C:/Users/marecm/PycharmProjects/try-ace-rabbitmq/example_4/consumer_4.py 26 1ca8e94a-f6d0-11e9-a1ae-8c04ba69e459 default 28036
2019-10-25 10:37:44,185 [INFO] Value: 19999 ; Delivery tag: 1400 C:/Users/marecm/PycharmProjects/try-ace-rabbitmq/example_4/consumer_4.py 26 1ca8e94a-f6d0-11e9-a1ae-8c04ba69e459 default 28036
2019-10-25 10:37:44,218 [INFO] Value: end ; Delivery tag: 1401 C:/Users/marecm/PycharmProjects/try-ace-rabbitmq/example_4/consumer_4.py 26 1ca8e94a-f6d0-11e9-a1ae-8c04ba69e459 default 28036
Interrupt
2019-10-25 10:37:44,221 [ERROR] Received 3386 messages. Not 20000. C:/Users/marecm/PycharmProjects/try-ace-rabbitmq/example_4/consumer_4.py 47 1ca8e94a-f6d0-11e9-a1ae-8c04ba69e459 default 28036

Process finished with exit code 0
```
It is interesting to notice that the consumer did not raise any connection error right after the broker went down. It 
seems that the consumer buffered hundreds of messages locally, although we did not set any Quality of Service (QoS),
allowing it to keep on working until all these messages are consumed. 
Notice that the consumer see the messages up to the value 996 before throwing the connection error message.

The consumer tries to reconnect to the broker until the broker is online again. This is desirable to improve consumer
reliability, as long as they are not blocking the process from performing other task.

After the broker goes online again, the first message logged by the consumer has value 8900. Messages with values 
in the range [997, 8899] are never printed by the consumer, which mean they were lost along the way.

## Conclusion
When the connection to the broker is lost, the railai-common consumer tries to re-connect to the broker. it will 
retry for as long as the broker is off-line. However, messages will be lost and are not recoverable. 


# Experiment 2: Consumer reliability with message acknowledgement.
Let's verify if we can fix the problem by acknowledging the messages on the consumer side.

producer_4_2.py is similar to producer_4.py except:
1) we replaced the publish() method with a publish_with_ack() method. publish_with_ack() is built with acknowledgement
  enabled, this is defined in the basic_consume() method by the no_ack parameter (set to False):
```python
    def consume_with_ack(self, callback):
        """
        This is the original method from the railai-common package
        :param callback:
        :param exchange:
        :param queue:
        :param routing_key:
        :return:
        """
        try:
            self.connection = pika.BlockingConnection(pika.URLParameters(self.uri))
            self.channel = self.connection.channel()
            self.channel.basic_consume(callback, queue=self.queue, no_ack=False)
            logger.info("Start consuming")
            self.channel.start_consuming()
```
  
2) The callback acknowledge the messages, with channel.basic_ack():
```python
    def callback(channel, method_frame, header_frame, body):
        val = json.loads(body.decode('utf-8'))['value']
        logger.info('Value: {} ; Delivery tag: {}'.format(val,
                                                          method_frame.delivery_tag))
        channel.basic_ack(method_frame.delivery_tag)
```

## Test Protocol
1) Purge the "tasks" queue in rabbitmq management console.
2) In the init file, set the number of producer to 1 and the number of messages per producer to 200.
3) Run the producer_4.py to publish 201 messages to the "tasks" queue.
4) Start consumer_4_2.py. while the consumer runs, stop/start the broker 2-3 times to simulates some disconnection.
5) Wait until the consumer completes. the consumers assert that 200 messages were delivered: no message were lost,
even when the broker went offline.

## Conclusion:
To prevent the loss of messages when the broker goes down, consumers must enable acknowledgement (no_ack=False, this 
is the default). Consumers must acknowledge messages in the call back method, so that the broker can remove te message
from the queue.



 