# Asynchronous style consumer
Pika provides a consumer implementation which works with asynchronous callback.

Let's run a first benchmark to check if it runs faster then the usual consumer implementation we met
so far, like in example_5.

# Asynchronous consumer benchmark

## Test
run consumer_7.py which is the benchmark for the asynchronous consumer. The benchmark measures how much time the 
consumer takes to consume 2000 messages (defined in init module):

```
QoS     run 1   run 2   run 3   run 4   run 5   average
100     0.26    0.26    0.33    0.25    0.31    0.28
300     0.25    0.29    0.26    0.23    0.23    0.25
500     0.24    0.26    0.31    0.59    0.33    0.34
700     0.26    0.28    0.36    0.29    0.24    0.28
900     0.24    0.28    0.30    0.28    0.24    0.27
1100    0.25    0.25    0.29    0.23    0.25    0.25
```

as a reminder, this is the benchmark of example_5 which run the same test with the blocking connection implementation:
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
it is hard to conclude anything, the values are too similar.

Let's run the same experience with 8000 messages.


## TEST 1
Here are the result of running the same benchmark as above with 8000 messages

with the asynchronous implementation:
QoS: 500; result: [1.3171938071746991, 1.5580931127340047, 1.876150515078617, 1.2563511240779413, 1.2887999429670742]
Average: 1.4593177004064672 seconds

with the blocking connection:
QoS: 500; runs: [1.899018774418572, 1.3586523162605406, 1.4337456698722484, 1.2769542688821645, 1.279655231636859]
average run: 1.4496052522140768 seconds

Once again, we can't draw any conclusion. Let's try with 80000 messages.

## TEST 2
Here are the result of running the same benchmark as above with 80000 messages.

with the asynchronous implementation:
QoS: 500; result: [8.744228386627075, 10.557217095619805, 10.357945885690043, 10.916972264498838, 10.698060880488981]
Average: 10.254884902584948

with the blocking connection:
QoS: 500; runs: [13.796474544195657, 13.085420309986915, 14.956375751932683, 14.743648875922048, 13.928411795014199]
average run: 14.102066255410302

## Conclusion
The asynchronous implementation of a consumer is significantly faster then the implementation with a blocking connection 
when the number of messages is in the order of 10s of thousands.

# TEST 3: asynchronous worker and task workload
So far, the callback method which process the message did not do much, it runs very fast and thus does not block the
main program execution for long. 

Let's now imagine a more realistic use case, where the callback actually takes as small amount of time to execute:
imagine that this is a call to a database that takes a few 100 of milliseconds, which block the execution of the main
program. 

let's test the asynchronous consumer with 2000 messages and a workload of 100 millisecond.

# Test
1) in the init file, set 5 producers, 400 messages per producer for a total of 2000 messages.
2) in the consumer_7.py module, find the on_message() method and uncomment the sleep of 100 milliseconds.
3) in the main program, set repeat to 1.
4) run the main program.

it takes 201 seconds for the consumer to process 2000 messages, roughly 100 ms per message which corresponds to the
workload duration. This will be our benchmark, for the future comparison.

## Conclusion
Running tasks synchronously in the asynchronous implementation of a worker significantly slows down the consumer.
To get the best of the asynchronous implementation, we must execute tasks asynchronously using a pool of workers.

# Test with thread pool of workers
consumer_7_1.py is similar to consumer_t.py except that the consumer introduces a ThreadPoolExecutioner to which 
the consumer delegates the tasks. The tasks takes 100 milliseconds to run (like in the previous test).

Try to run the benchmark consumer_7_1.py with various pool size.

1) in the init file, set 5 producers, 400 messages per producer for a total of 2000 messages.
2) set the _worker_count to 1 in the init method of the consumer_7_1.py module. _worker_count defines the 
number of worker in the pool.

run the test with various worker pool size. Below are the results i obtained when i ran the test:
```
messages    worker count    load    result (Seconds)
2000        1               0.1     201             # similar to example_7 without pool of worker.
2000        2               0.1     100
2000        3               0.1     67
2000        8 (os.cpu_count)0.1     25
2000        16              0.1     13
2000        32              0.1     9
```
## Conclusion
Using a worker pool to execute tasks asynchronously speed up consumer dramatically. with a workload of 100ms, and with
8 workers in the pool, the speed is increased 8 times.

Because the task is not compute intensive, we can see that 16 workers still scales linearly: 201/16=12.5#13seconds. This
is  not true anymore with 32 workers, where we would expect 6 seconds, instead of 9 seconds, if it had scaled linearly.

Choosing the right number of workers will depend on your hardware and on the type of task. I/O intensive task can use 
more workers then compute intensive task.