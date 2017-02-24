# This file contains the configuration variables shared across the application

import os
import sys
import time
from redis_config_type import RedisConfigType
from process_lock_value_type import ProcessLockValueType
from leader_elector import LeaderElector
from threading import Thread


redis_hostname = '127.0.0.1'
redis_port = 6379
redis_db = 0

redis_config = RedisConfigType(redis_hostname, redis_port, redis_db)

service_fqdn = '127.0.0.1'
service_port = 5000
service_pid = os.getpid()

process_lock_value = ProcessLockValueType(service_fqdn, service_pid, service_port)

app_name = 'cacher'

process_lock_ttl_sec = 15

retry_interval_ms = 100

leader_elector = LeaderElector(redis_config=redis_config,
                               app_name=app_name,
                               process_lock_value=process_lock_value,
                               process_lock_ttl=process_lock_ttl_sec,
                               retry_interval_ms=retry_interval_ms)


def heartbeat():
    while True:
        leader = leader_elector.get_leader()
        print leader.__dict__
        time.sleep(5)

t = Thread(target=heartbeat)


def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        t.join()
        sys.exit(0)


