#~~Highly~~ ~~available~~ Horizontally scalable caching service
This is my attempt at putting together a simple, horizontally scalable, caching
service. The current behavior of this service is a bit peculiar, in that the
keys that you want to cache must be registered with the service at startup. At
this time entries can only be added or removed by reconfiguring and restarting 
the service. Although, this is the current behavior, adding the ability to 
register more keys at runtime is trivial. Also, one may quite easily implement 
the 'remove' functionality.

##Dependencies
I've built and tested this service on Linux (Ubuntu 16.04.2 LTS) on a 64-bit
platform with the following:

1. [Python 2.7.12](https://www.python.org/downloads/)
1. [Pip 9.0.1](https://pip.pypa.io/en/stable/installing/)
1. [Redis server 3.2.7](https://redis.io/topics/quickstart)
1. [Virtualenv 15.0.1](https://virtualenv.pypa.io/en/stable/installation/)


##Installation

1. Clone the repository

   ```
   git clone https://github.com/dg321123/cache.git
   ```
   
1. Set up the virtual environment
   ```
   cd cache
   virtualenv venv
   ```

1. Activate the virtual environment

   ```
   source venv/bin/activate
   ```

1. Install the package dependencies

   ```
   pip install requirements.txt
   ```

1. Make sure that you have the GIT_HUB_API_TOKEN environment variable set. You
   can generate the token at https://github.com/settings/tokens. Then export 
   the token using

   ```
   export GITHUB_API_TOKEN=<Token>
   ```
Ideally add this to your startup script.

1. Start the redis server. Installation guidelines for Redis are at 
   https://redis.io/topics/quickstart. The README.md file has necessary 
   information regarding configuring and starting up an instance. 

1. The service uses the following configuration for Redis

   ```
   redis_hostname = '127.0.0.1'
   redis_port = 6379
   redis_db = 0
   ```
   If your values for the hostname, port or db are different update them in
   `app_config.py`

1. Now you are ready to start the service using
   ```
   python service.py -p <port number>
   ```
   
## Known issues / Design choices
1. It is necessary to wait for the leadership record in Redis to be fresh 
   before the process can be brought up successfully, since at start up the 
   record refreshes its cache. 
   
1. The code is tightly coupled to Redis. Ideally, there should have been an
   interface so that replacing Redis with another key value pair would be 
   simpler.
   
1. The /healthcheck is representative of 
    1. the success / failure of the connection while processing the most recent
       request and 
    1. also the success / failure of the call to find the leader. 
    
   This means that if the service is reporting that it is unhealthy due to 
   connection failure while getting results from say github it will continue to
   do so until the connection is successfully established for another request. 
   Therefore, we can add process to probe the service when it reports 
   healthcheck failures. 
   
   Healthcheck failures due to the failure to find the leader auto reset when 
   the leader is successfully determined because the service periodically polls
   Redis for this information. 
   
1. The leadership implementation is highly simple and critically dependent on 
   the availability of the database. One may look into Paxos or 
   [Raft](https://raft.github.io/) for leader election algorithms without single
   point for failure.
   
1. As a design choice, I've chosen to return a stale entry when proxing the 
   request via the leader or github fails. This may not be what you want for 
   your usecase. If so, you can modify cache.py to comment out the following 
   
   ```python
   # If the request failed, should we return what we have? Only if we were
   # able to refresh the value for the key at least once.
   if status_code != 200 and attributes.refreshed:
       logger.debug('Request failed. Returning stale entry')
       status_code = 200
   ```
   
1. The fact that heartbeat for leader elector and the method for signal handler
   are in `app_config.py` is *ugly*. This *must* be corrected. In fact leader 
   elector must be a singleton in this context with static methods.
   
1. The tests in api_test_suite.sh are very fragile. Ideally, the calls to the 
   golden source (api.github.com) should be mocked so that the test data does 
   not change. Also, mocking will make it possible for us to see how the 
   service behaves with changing data (does it actually refresh cache?).
   
1. Logging could be better configured. I should look into the best practices 
   for logging in Python. Currently, only once process's log goes into the log
   file which is not very useful. If you happen to run multiple instance of 
   the service on the same machine, the logs for other instances are lost. For 
   now, one can redirect stdout and stderr to a file at the time of starting 
   the server. 
   
1. It would be nice if the service emitted metrics about say the latency so we
   could measure the performance p50, p99, p100 etc. This should also be fairly
   simple. We need to use the constructor destructor concept which starts the 
   clock in the constructor and stop and emits the metric in the destructor.
   
