#Highly available caching service
This is my attempt at putting together a simple, highly available, caching
service. The current behavior of this service is a bit peculiar, in that the
keys that you want to cache must be registered with the service at startup. No
entries can be added or removed at a later time without reconfiguring and
restarting the service. Although, this is the behavior at this time, adding the
ability to register more keys at runtime is trivial. Also, one may quite easily
implement the 'remove' functionality.

##Dependencies
I've built and tested this service on Linux (Ubuntu 16.04.2 LTS) on a 64-bit
platform with the following:

1. Python 2.7.12
1. pip 9.0.1
1. Redis server v=3.2.7
1. virtualenv 15.0.1


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

1. Start the redis server

   ```
   redis-server&
   ```

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