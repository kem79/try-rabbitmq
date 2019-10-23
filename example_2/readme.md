# Producer Pool with Global RabbitMQ client
This experiment will demonstrate that it is not advisable to share a rabbit mq connection in the global
scope with a pool of multi-threaded producers.

## Test presentation
producer_2.py creates several publishers. The number of publishers is defined by producer_count
 (defined in the __init__.py). Each publisher runs in its own thread. Each producer publishes 
a number of messages equal to message_count_per_producer (defined in the __init__.py) and stops.

The consumer (consumer_2.py) counts the number of received messages and assert that this count equals the number
of messages sent by all the producers. 

The purpose is, once again, to verify that all messages sent by producers are 
successfully received by the consumer, i.e. no message loss.

You may have noticed that the rabbitmq client is created in the global space without any consideration for 
thread safety: 2 threads can potentially grab the connection at the same time to send a message, 
with unpredictable outcome... let's verify this in the first experiment.

## Test Protocol
1) Start the consumer.py.

2) Run producer_2.py with 10 producers and 1000 messages (in init file), you should witness exceptions in the trace. if not,
 increase these values:
```
2019-10-22 17:15:04,419 [INFO] publishing...{"value": 634} C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py 111 67c0b7a8-f4ac-11e9-97d1-8c04ba69e459 default 18800
2019-10-22 17:15:04,419 [INFO] publishing...{"value": 630} C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py 111 67c0b7a9-f4ac-11e9-9700-8c04ba69e459 default 18800
2019-10-22 17:15:04,433 [ERROR] AMQPError occurs, retry connection with exchange=tasks C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py 121 67c0dc94-f4ac-11e9-92d1-8c04ba69e459 default 18800
Traceback (most recent call last):
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py", line 118, in publish2
    headers={'x-trace-id': trace_id}))
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 2077, in basic_publish
    mandatory, immediate)
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 2164, in publish
    self._flush_output()
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 1250, in _flush_output
    *waiters)
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 474, in _flush_output
    result.reason_text)
pika.exceptions.ConnectionClosed: (505, 'UNEXPECTED_FRAME - expected method frame, got non method frame instead')
Exception in thread Thread-2:
Traceback (most recent call last):
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\base_connection.py", line 417, in _handle_read
    data = self.socket.recv(self._buffer_size)
BrokenPipeError: [WinError 10058] A request to send or receive data was disallowed because the socket had already been shut down in that direction with a previous shutdown call

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\marecm\AppData\Local\Programs\Python\Python35\lib\threading.py", line 914, in _bootstrap_inner
    self.run()
  File "C:\Users\marecm\AppData\Local\Programs\Python\Python35\lib\threading.py", line 862, in run
    self._target(*self._args, **self._kwargs)
  File "C:/Users/marecm/PycharmProjects/try-ace-rabbitmq/example_2/producer_2.py", line 17, in publish
    message=json.dumps({'value': i}))
  File "<C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\decorator.py:decorator-gen-6>", line 2, in publish2
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\retry\api.py", line 74, in retry_decorator
    logger)
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\retry\api.py", line 33, in __retry_internal
    return f()
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\traceable_logger.py", line 57, in __decorated_func_with_self
    return func(self, *args, **kwargs)
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py", line 118, in publish2
    headers={'x-trace-id': trace_id}))
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 2077, in basic_publish
    mandatory, immediate)
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 2164, in publish
    self._flush_output()
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 1250, in _flush_output
    *waiters)
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 455, in _flush_output
    self._impl.ioloop.poll()
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\select_connection.py", line 245, in poll
    self._poller.poll()
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\select_connection.py", line 718, in poll
    self._dispatch_fd_events(fd_event_map)
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\select_connection.py", line 625, in _dispatch_fd_events
    handler(fileno, events)
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\base_connection.py", line 395, in _handle_events
    self._handle_read()
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\base_connection.py", line 440, in _handle_read
    return self._handle_error(error)
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\base_connection.py", line 368, in _handle_error
    repr(error_value))
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\connection.py", line 1974, in _on_terminate
    self._adapter_disconnect()
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\select_connection.py", line 110, in _adapter_disconnect
    self.ioloop.remove_handler(self.socket.fileno())
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\select_connection.py", line 202, in remove_handler
    self._poller.remove_handler(fileno)
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\select_connection.py", line 415, in remove_handler
    del self._fd_handlers[fileno]
KeyError: 288

2019-10-22 17:15:04,441 [INFO] publishing...{"value": 635} C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py 111 67c0b7a8-f4ac-11e9-97d1-8c04ba69e459 default 18800
2019-10-22 17:15:04,446 [ERROR] AMQPError occurs, retry connection with exchange=tasks C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py 121 67c0b7a8-f4ac-11e9-97d1-8c04ba69e459 default 18800
Traceback (most recent call last):
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py", line 118, in publish2
    headers={'x-trace-id': trace_id}))
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 2077, in basic_publish
    mandatory, immediate)
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 2163, in publish
    immediate=immediate)
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\channel.py", line 415, in basic_publish
    raise exceptions.ChannelClosed()
pika.exceptions.ChannelClosed
2019-10-22 17:15:06,445 [INFO] publishing...{"value": 625} C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py 111 67c0dc94-f4ac-11e9-92d1-8c04ba69e459 default 18800
2019-10-22 17:15:06,449 [ERROR] AMQPError occurs, retry connection with exchange=tasks C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py 121 67c0dc94-f4ac-11e9-92d1-8c04ba69e459 default 18800
Traceback (most recent call last):
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py", line 118, in publish2
    headers={'x-trace-id': trace_id}))
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 2077, in basic_publish
    mandatory, immediate)
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 2163, in publish
    immediate=immediate)
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\channel.py", line 415, in basic_publish
    raise exceptions.ChannelClosed()
pika.exceptions.ChannelClosed
2019-10-22 17:15:06,457 [INFO] publishing...{"value": 635} C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py 111 67c0b7a8-f4ac-11e9-97d1-8c04ba69e459 default 18800
2019-10-22 17:15:06,462 [ERROR] AMQPError occurs, retry connection with exchange=tasks C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py 121 67c0b7a8-f4ac-11e9-97d1-8c04ba69e459 default 18800
Traceback (most recent call last):
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py", line 118, in publish2
    headers={'x-trace-id': trace_id}))
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 2077, in basic_publish
    mandatory, immediate)
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 2163, in publish
    immediate=immediate)
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\channel.py", line 415, in basic_publish
    raise exceptions.ChannelClosed()
pika.exceptions.ChannelClosed
2019-10-22 17:15:10,060 [INFO] publishing...{"value": 625} C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py 111 67c0dc94-f4ac-11e9-92d1-8c04ba69e459 default 18800
Exception in thread Thread-3:
Traceback (most recent call last):
  File "C:\Users\marecm\AppData\Local\Programs\Python\Python35\lib\threading.py", line 914, in _bootstrap_inner
    self.run()
  File "C:\Users\marecm\AppData\Local\Programs\Python\Python35\lib\threading.py", line 862, in run
    self._target(*self._args, **self._kwargs)
  File "C:/Users/marecm/PycharmProjects/try-ace-rabbitmq/example_2/producer_2.py", line 17, in publish
    message=json.dumps({'value': i}))
  File "<C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\decorator.py:decorator-gen-6>", line 2, in publish2
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\retry\api.py", line 74, in retry_decorator
    logger)
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\retry\api.py", line 33, in __retry_internal
    return f()
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\traceable_logger.py", line 57, in __decorated_func_with_self
    return func(self, *args, **kwargs)
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py", line 118, in publish2
    headers={'x-trace-id': trace_id}))
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 2077, in basic_publish
    mandatory, immediate)
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 2163, in publish
    immediate=immediate)
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\channel.py", line 415, in basic_publish
    raise exceptions.ChannelClosed()
pika.exceptions.ChannelClosed

2019-10-22 17:15:10,065 [ERROR] AMQPError occurs, retry connection with exchange=tasks C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py 121 67c0dc94-f4ac-11e9-92d1-8c04ba69e459 default 18800
Traceback (most recent call last):
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py", line 118, in publish2
    headers={'x-trace-id': trace_id}))
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 2077, in basic_publish
    mandatory, immediate)
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 2163, in publish
    immediate=immediate)
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\channel.py", line 415, in basic_publish
    raise exceptions.ChannelClosed()
pika.exceptions.ChannelClosed
Exception in thread Thread-1:
Traceback (most recent call last):
  File "C:\Users\marecm\AppData\Local\Programs\Python\Python35\lib\threading.py", line 914, in _bootstrap_inner
    self.run()
  File "C:\Users\marecm\AppData\Local\Programs\Python\Python35\lib\threading.py", line 862, in run
    self._target(*self._args, **self._kwargs)
  File "C:/Users/marecm/PycharmProjects/try-ace-rabbitmq/example_2/producer_2.py", line 17, in publish
    message=json.dumps({'value': i}))
  File "<C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\decorator.py:decorator-gen-6>", line 2, in publish2
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\retry\api.py", line 74, in retry_decorator
    logger)
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\retry\api.py", line 33, in __retry_internal
    return f()
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\traceable_logger.py", line 57, in __decorated_func_with_self
    return func(self, *args, **kwargs)
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py", line 118, in publish2
    headers={'x-trace-id': trace_id}))
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 2077, in basic_publish
2019-10-22 17:15:10,811 [INFO] publishing...{"value": 635} C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py 111 67c0b7a8-f4ac-11e9-97d1-8c04ba69e459 default 18800
    mandatory, immediate)
2019-10-22 17:15:10,815 [ERROR] AMQPError occurs, retry connection with exchange=tasks C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py 121 67c0b7a8-f4ac-11e9-97d1-8c04ba69e459 default 18800
Traceback (most recent call last):
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py", line 118, in publish2
    headers={'x-trace-id': trace_id}))
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 2163, in publish
    immediate=immediate)
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\channel.py", line 415, in basic_publish
    raise exceptions.ChannelClosed()
pika.exceptions.ChannelClosed

  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 2077, in basic_publish
    mandatory, immediate)
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 2163, in publish
    immediate=immediate)
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\channel.py", line 415, in basic_publish
    raise exceptions.ChannelClosed()
pika.exceptions.ChannelClosed
ending...
```
Notice a first thread runs into some weird exception. Something wrong happened when the thread tries to read
or write to the socket connection. This is a typical error message you will experience when having concurrency
issue with threads.
We can see that all 3 threads eventually run into AMQPError which is handled by the retry mechanism. But the publish2()
 method is purged from connection/channel management, so all 3 threads stop at once.
 
 The consumer process should return an AssertionError as the count of messages calculated by the consumer 
 is not the same as the count of message sent by the producers.
 
## Conclusion
We should never share a connection from the global scope with a pool of threads without any thread safety mechanism. 
Generally speaking, this experiment also demonstrate that we should never share a object from the global scope with 
a pool of thread, except if the share object is certified thread safe.

When replacing multi-threading with multi-processing in the main of producer_2.py, there is no exception anymore:
the rabbitmq client instance can be "shared" to multiple processes without any problem. This is true because of Python
mechanism of forking processes and the inherent management of the parent and children memory space. Basically,
each child get a copy of the rabbitmq client instance in their global space, the children changes to their global space are not 
visible from the parent global space, so there can't be any interference.

## Producer Pool with Secured Connection Sharing
To Fix the concurrency issue, the most simple way is to use a lock to secure the rmq connection. producer_2_1.py
shows how to do that.

Start the consumer.py. Start the producer_2_1.py. The consumer assert the right count of message.
 You should witness no exception. The lock prevents concurrent access to the rmq client, at a performance cost of
  course: threads now have to wait for the critical part of code to be accessible. 
  
It would be interesting to check the result of creating one channel per thread on 1 single channel.


let's switch to another topic now that we know how to handle connections, this is the topic of publisher
message delivery confirm.

# Example 2: Producer message delivery

## Test Introduction
Producer "delivery confirm" ensures that the broker acknowledges messages sent by the producer. This
is necessary to ensure that all messages sent by producers reach the broker and are not lost on the way.
let's have a look at the effect of this parameter.

producer_2_2.py is similar to the producer you already met in the past examples, except that the channel is configured
 to confirm producer message delivery.
 ```
channel.confirm_delivery()
```

## Test Protocol
### without delivery confirm
in the publish3() methods in ace_rabbitmq.py, ensure that the line which confirms delivery is commented:
```
# channel.confirm_delivery()
```
run producer_2_2.py and stop/start the rabbitmq broker of your vagrant project. Without delivery confirm,
the broker will receive less messages then expected.

1) in the init file, set 10 producers and 300 messages. The broker expects to get 3001 messages (3000 + 1 death pill)
2) ssh into the vagrant box and stop/start the broker. stopping the broker should eventually drop some messages.
```
vagrant ssh
sudo docker stop rabbtimq
sudo docker start rabbitmq
```
3) log into the rabbitmq management console and go to the "tasks" queue. 
```
http://192.168.99.100/15672
```
You should witness that the number of messages in the "tasks" queue is largely less then 3001. When i run the 
experiement, I stopped the broker once and i witnessed that there were only 2160 message in the broker, far less then
 3001.
 
Let's see if enabling delivery confirm improve something.

### with delivery confirm
1) Purge the queue in the rabbitmq management console (around the bottom of the page).
```
http://192.168.99.100/15672
```
Verify that there are no message in the queue.

2) in the publish3() methods in ace_rabbitmq.py, ensure that the line which confirms delivery is NOT commented:
```
channel.confirm_delivery()
```
For the rest of the steps, refer to the steps of the last experience. run the producer_2_2.py and stop/start the broker
 a few times. i stopped it 3 times during my experience.
 
In the rabbitmq management console, you should notice that there are at least 3001 messages, none are lost. 
During my experience, i noticed 3005 messages in the queue. There are 4 more messages then expected. i ran the experience 
a second time and there were 3 more messages. I cannot confirm why there are a few more messages then expected. However,
 it means that some messages might be published twice to the queue, so the message consumer must be ready
to consume the same message twice, in which case the result should be the same: the operation should be idempotent.

### Conclusion: 
We should always enable message delivery confirm with producers to ensure that all the messages eventually reached the 
broker and get a chance to be delivered to the consumer. Messages will eventually appears more than once in the queue,
which means that consumer should be idempotent.

