# Quality of Service (QoS)
The consume() method configure the Quality of Service (QoS) for the channel. The QoS allows to define how many 
un-acknowledge messages to pre-fetch from the broker and to keep in memory near the consumer. This is to improve
consumer performance, as we can save the round trip to the broker by buffering messages locally. The QoS has to be set 
empirically, it is usually in the 100s magnitude, i.e. 300-400.

Let's play with the consume() method of railai-common and the QoS parameter.

# Experiment 1: QoS with acknowledgement
producer_5.py contains a benchmark to measure the speed of the consumer.

## Test
1) Set the QoS to 100 in consumer_5.py
2) set 1000 messages, 1 producer in the init file.
3) run consumer_5.py. it will run the produce/consume cycle 3 times.

You should experience a trace similar to the one below:
```
purge messages
Start...
2019-10-28 15:38:19,068 [INFO] Publish 1000 messages. C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\example_5\producer_5.py 19 e9222ac2-f955-11e9-b311-8c04ba69e459 default 7332
...
2019-10-28 15:38:22,226 [INFO] Received 1000 messages C:/Users/marecm/PycharmProjects/try-ace-rabbitmq/example_5/consumer_5.py 53 e9222ac2-f955-11e9-b311-8c04ba69e459 default 7332
2019-10-28 15:38:22,229 [INFO] Publish 1000 messages. C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\example_5\producer_5.py 19 e9222ac2-f955-11e9-b311-8c04ba69e459 default 7332
2019-10-28 15:38:23,645 [INFO] Building consume connection exchange=tasks, queue=tasks C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py 60 e9222ac2-f955-11e9-b311-8c04ba69e459 default 7332
2019-10-28 15:38:23,663 [INFO] Start consuming C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py 76 e9222ac2-f955-11e9-b311-8c04ba69e459 default 7332
Interrupt
2019-10-28 15:38:23,801 [ERROR] Received 900 messages. Not 1000. C:/Users/marecm/PycharmProjects/try-ace-rabbitmq/example_5/consumer_5.py 51 e9222ac2-f955-11e9-b311-8c04ba69e459 default 7332
runs: [0.21178820909048685, 0.16558019661237378, 0.16134917437277307]
average run: 0.17957252669187787

Process finished with exit code 0
```

Run the same experiment with QoS value 300:
```
purge messages
Start...
2019-10-28 15:42:01,929 [INFO] Publish 1000 messages. C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\example_5\producer_5.py 19 6df8aa5a-f956-11e9-b3bd-8c04ba69e459 default 14616
...
2019-10-28 15:42:05,041 [INFO] Received 1000 messages C:/Users/marecm/PycharmProjects/try-ace-rabbitmq/example_5/consumer_5.py 53 6df8aa5a-f956-11e9-b3bd-8c04ba69e459 default 14616
2019-10-28 15:42:05,045 [INFO] Publish 1000 messages. C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\example_5\producer_5.py 19 6df8aa5a-f956-11e9-b3bd-8c04ba69e459 default 14616
2019-10-28 15:42:06,649 [INFO] Building consume connection exchange=tasks, queue=tasks C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py 60 6df8aa5a-f956-11e9-b3bd-8c04ba69e459 default 14616
2019-10-28 15:42:06,672 [INFO] Start consuming C:\Users\marecm\PycharmProjects\try-ace-rabbitmq\common\ace_rabbitmq.py 76 6df8aa5a-f956-11e9-b3bd-8c04ba69e459 default 14616
Interrupt
2019-10-28 15:42:06,777 [ERROR] Received 700 messages. Not 1000. C:/Users/marecm/PycharmProjects/try-ace-rabbitmq/example_5/consumer_5.py 51 6df8aa5a-f956-11e9-b3bd-8c04ba69e459 default 14616
runs: [0.17516021607702037, 0.16927221448701157, 0.1324848965360057]
average run: 0.1589724423666792
```
it is interesting to notice that the last run always fail, the consumer miss a few messages which is equal to the 
QoS  value.

## Conclusion
Increasing the QoS make the consumer faster. However, some messages are lost. I will not spend time to investigate why. 

## Comment on railai-common consume() implementation.
consume() implementation has a major impact on the effect of setting QoS: The channel and the QoS are reset every 
time a new message come in, probably reducing, if not nullifying, the effect of the QoS.

Let's create another consume() method which handle the channel creation and the QoS setting outside the consume()
method and re-run the experiment. Does the consumer run faster?

# Experiment 2: QoS with connection/channel creation in init file.
consumer_5_1.py is similar to consumer_5.py except that the connection, the channel and the QoS are initialized in 
the init method. the consumer uses one single channel to consume all the messages. The QoS will ensure that a defined amount 
of messages are queued locally to save round trip and accelerate the consumer speed, thus improving performance.

## Test
1) set the QoS to the desired value
2) set the number of messages to 2000.
3) run consumer_5_1.py which benchmarks consume() for Qos in [100, 300, 500, 700, 900, 1100, 1300].
Here are the results when i run the experiment:
```
Qos     run 1   run2    run 3    run 4   run 5   avg
100     0.36    0.34    0.30    0.32    0.3     0.32
300     0.34    0.29    0.27    0.32    0.24    0.29
500     0.31    0.27    0.4     0.17    0.14    0.26
700     0.33    0.30    0.18    0.15    0.14    0.21
900     0.29    0.25    0.16    0.14    0.17    0.20
1100    0.30    0.23    0.13    0.18    0.13    0.19
1300    0.32    0.22    0.13    0.16    0.13    0.19
```
Notice:
1) all the messages published by the producer are consumed by the consumer. no more, no less.
2) the speed increase when the QoS increase. we reach a plateau at 1100 prefetch messages.
3) the fastest run is 0.13/0.14 ms. it is reached at QoS equal to 500, before QoS equal 1100.

## Conclusion:
The consumer performance can be drastically improved by re-using a channel and setting a proper QoS in the magnitude 
of several hundreds. A good choice would be a value between 500 and 1100 for our particular case.

