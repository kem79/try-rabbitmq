# multi-channel
LEt's see if we can scale consumer. let's build a test with 2 consumers, each with its own channel of top of 
one blocking connection.

# Experiment 1: 2 consumers on one channel with channel wide QoS
i tried using 2 channels on top of one blocking connection, but it does not work.

pika throws an exception:
```
Exception in thread Thread-2:
Traceback (most recent call last):
  File "C:\Users\marecm\AppData\Local\Programs\Python\Python35\lib\threading.py", line 914, in _bootstrap_inner
    self.run()
  File "C:\Users\marecm\AppData\Local\Programs\Python\Python35\lib\threading.py", line 862, in run
    self._target(*self._args, **self._kwargs)
  File "C:/Users/marecm/PycharmProjects/try-ace-rabbitmq/example_6/consumer_6.py", line 87, in consume
    channel.start_consuming()
  File "C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\venv\lib\site-packages\pika\adapters\blocking_connection.py", line 1775, in start_consuming
    'start_consuming may not be called from the scope of '
pika.exceptions.RecursionError: start_consuming may not be called from the scope of another BlockingConnection or BlockingChannel callback
```

## Conclusion
It is not possible to create 2 consumers with one blocking connection to scale up message consumer.
The only way to work with blocking connection is to create 1 connection and 1 channel per consumer thread/process.

The best option to scale consumer is to use a thread pool to delegate tasks in the callback() method. This is the topic
of example_7


