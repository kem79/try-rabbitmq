# Producer Reliability
Let's experiment with producer reliability. What happens if the connection between the producer and the broker
 is broken? if the channel is broken?
 
# Experiment 1
let's verify the effect of the broker going down on the publish() method.

## test protocol
1)  start the producer_1.py, this module create a producer which emits messages every 2 seconds.
2) stop the broker while the producer is still running:
```
vagrant ssh
sudo docker stop rabbitmq
```

## Observations
When the connection goes down, the producer tries to reconnect 3 times. If the producer cannot connect successfully the third
time, it throws an error and stop. The retry count being only 3, and the period of time during 2 retries being only a 
few seconds, the producer cannot endure a long disconnection.

### Is it advisable to retry the connection forever?
Retrying has a major drawback: the producer runs in a dead loop, preventing the process of new request. If the 
shortage is long and the producer retries forever, the web server can eventually go overboard and crash. We need
 a better fail safe approach for this type of scenario, like storing the message to another storage and replay these 
 messages later (Like Sunny implemented it in a micro-service).

### On the matter of connection and channel lifecycle
On a side note, the connection is created and tore-down every time the publish() method is called. The same can be said for the channel.
This is not desirable and not advised by Rabbitmq documentation because creating connection is costly in term of time
and memory (especially on the broker side). Rabbitmq documentation advises to create 1 connection per
per process. If multi-threading is used, then each thread should have its own channel.
     
### Conclusion
This is my personal conclusion, it only engages myself.

#### For a Flask application with one single process (no multiprocessing, no multi-threading).
Each Flask application should have its own connection.

One connection with short retry is enough. The retry should be short to prevent producers from blocking the main 
process execution.

If the connection cannot be established after the final retry, the message should be persisted somewhere else 
(Mongo, not redis) so that the message can be re-queued once the broker is online.

There is no need for a connection pool: there is only one process, only one connection is needed.
 
 