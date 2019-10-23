# Rabbitmq Reliability
This repository contains several experiences which aim at assessing the reliability of delivering and 
consuming messages with the ACE module rabbitmq.py that is part of the railai_common library.

We will try to understand how Pika, the underlying Python library that we use to interact with a rabbitmq
broker, work. We will have a look at message producer, consumers, connection, channels and the effect of
a rabittmq broker going off-line. In each case, we will try to answer the question: "Do we drop some messages?".

# Packages Introduction
Here is an introduction to the various packages of this project:

- common contains the re-usable code that ACE uses in the micro-services to interact with rabbitmq. it contains
a copy of the rabbitmq.py module (copied from railai-common lib) which contains the original consume() and
and publish() methods of various flavor (without connection creation, without message delivery).

- example_1 tests the effect of a rabbitmq server going off-line on the publish() method of rabbitmq.py

- example_2 tests the effect of sharing a connection which is not thread safe with a pool of producers. it will 
also show a simple way to make the connection thread safe. In a second part, it will show the effect of 
using message delivery to ensure all message produced by producer reach the broker. 

- example_3 is a performance benchmark. You can run the module to show the performance impact of 
creating a connection in every publish() call, and the impact of logging message.

# Pre-requisite
Ensure that your rabbitmq broker is running in you vagrant box. if so, you should be able
to access the management console:
```
http://192.168.99.100:15672
```
if this is not the case, clone 'rails-service-appliance' repository and run:
```
vagrant up
```