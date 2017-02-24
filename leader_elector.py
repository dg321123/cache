import datetime
import json
import logging
import time

import redis

import unmarshal_json

from process_lock_value_type import ProcessLockValueType


class LeaderElector:
    def __init__(self, redis_config, app_name, process_lock_value, process_lock_ttl, retry_interval_ms=100):
        self.redis_config = redis_config
        self.process_lock_key = 'Dist lock ' + app_name
        self.process_lock_value = process_lock_value
        self.process_lock_ttl = process_lock_ttl
        self.retry_interval_ms = retry_interval_ms
        self.redis_pool = redis.ConnectionPool(host=self.redis_config.hostname,
                                               port=self.redis_config.port,
                                               db=self.redis_config.db)
        self.time_to_refresh = datetime.datetime(1970, 1, 1)
        self.current_leader = ''

    def get_leader(self):
        # If the key is not yet set to expire, there is no point retrying now.
        # This is bound to lead to thundering herd problem. However, it's still
        # better than hitting the DB more often.
        logging.debug(self.time_to_refresh)
        if datetime.datetime.now() < self.time_to_refresh:
            logging.debug('Returning from cache.')
            return self.current_leader

        logging.debug('Checking redis')

        # Get a handle to Redis
        r = redis.Redis(connection_pool=self.redis_pool)

        succeeded = False
        decoded_process_lock_value = ''
        retries = 1

        time_to_refresh_delta = 0

        while not succeeded:
            # conditionally write only if doesn't already exist. If we succeed, we will be the leader, else we must find
            # out who the leader is.
            is_leader = r.set(self.process_lock_key, json.dumps(self.process_lock_value.__dict__),
                              ex=self.process_lock_ttl, nx=True)
            time_to_refresh_delta = datetime.timedelta(seconds=self.process_lock_ttl)
            logging.debug('is_leader = ' + str(is_leader))

            if not is_leader:
                # If set didn't succeed, read the value and decode it.
                process_lock_value_string = r.get(self.process_lock_key)
                decoded_process_lock_value = unmarshal_json.decode_json_dump(process_lock_value_string)

                # If this process is the leader, update the expiry of the record in the database,
                # else update this process's time whem it must refresh the leadership record.
                if decoded_process_lock_value.__dict__ == self.process_lock_value.__dict__:
                    is_leader = True
                    r.expire(self.process_lock_key, self.process_lock_ttl)
                else:
                    ttl = r.ttl(self.process_lock_key)
                    time_to_refresh_delta = datetime.timedelta(seconds=ttl)

            if is_leader or isinstance(decoded_process_lock_value, ProcessLockValueType):
                succeeded = True
                retries = 1

            # If we failed to determine leadership, back-off and retry.
            if not succeeded:
                logging.info('Did not succeed in getting a leader. Will retry')
                retries *= 2
                time.sleep(self.retry_interval_ms * retries / 1000)

        # Now that we have determined the leader, update the local parameters.
        self.time_to_refresh = datetime.datetime.now() + time_to_refresh_delta

        if is_leader:
            self.current_leader = self.process_lock_value
        else:
            self.current_leader = decoded_process_lock_value

        return self.current_leader
