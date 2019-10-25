# Effect of broker connection on performance
In previous example, we mentioned that creating connection and channel every time we publish a 
message is not advisable because creating a connection slows down the publication of message.
Let's demonstrate this with a benchmark.

This package contains 2 modules:
- one module to benchmark publish(), the original method from railai-common
- one module to benchmark publish2(), which is the same as publish() except that i removed the connection and channel
creation (they are created in the init method).

# Test
Run the 2 modules to compare the timings.

producer with connection: 
```
runs: [3.8169565654154374, 3.786254986319688, 3.7051593083908436]
average: 3.769456953375323
```

producer without connection
```
runs: [1.450973392252828, 1.4379962691040986, 1.4281564902358328]
average: 1.4390420505309198
```

Calling connect() in the publish() method reduce speed by roughly 2.7 times.

producer_2_1.py with the calls to logging.info() and logging.debug() commented in the publish2() method:
```
runs: [0.011703066485342677, 0.011211590621128278, 0.011410881383650383]
average: 0.011441846163373778
```
Calling publish() without calling connect() and without logging messages is 350 times faster than publish() method 
of th railai-common package. It would be interesting to use an asynchronous logger to improve performance.

# Conclusion:
We should manage the connection and the channel outside the publish() method to improve the performance.
This can be done in several ways: using try/except, or using an event loop with callback (preferable).
We should also wisely log messages and use an asynchronous logging library to improve performance.

