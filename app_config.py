# This file contains the configuration variables shared across the application

import os
import sys
import time
from redis_config_type import RedisConfigType
from process_lock_value_type import ProcessLockValueType
from leader_elector import LeaderElector
from threading import Thread

# Redis configuration
redis_hostname = '127.0.0.1'
redis_port = 6379
redis_db = 0

redis_config = RedisConfigType(redis_hostname, redis_port, redis_db)

# Configuration of the service
service_fqdn = '127.0.0.1'
service_port = 5000
service_pid = os.getpid()

process_lock_value = ProcessLockValueType(service_fqdn, service_pid, service_port)

# Cacher configuration
golden_source = 'api.github.com'
max_time_to_expiry_seconds = 10
leader_timeout = 3
slave_timeout = 0.1

# Leader election configuration
app_name = 'cacher'
process_lock_ttl_sec = 15
process_lock_heartbeat_interval_sec = 5
retry_interval_ms = 100

leader_elector = LeaderElector(redis_config=redis_config,
                               app_name=app_name,
                               process_lock_value=process_lock_value,
                               process_lock_ttl=process_lock_ttl_sec,
                               retry_interval_ms=retry_interval_ms)


terminate_leader_elector_hb = False


def heartbeat():
    while True and not terminate_leader_elector_hb:
        leader = leader_elector.get_leader()
        print leader.__dict__
        time.sleep(process_lock_heartbeat_interval_sec)


t = Thread(target=heartbeat)


def signal_handler(signal, handler):
        global terminate_leader_elector_hb
        terminate_leader_elector_hb = True
        t.join(None)
        sys.exit(0)
