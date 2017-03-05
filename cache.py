import app_config
from datetime import datetime, timedelta
from cache_exceptions import KeyMissingFromCacheException
from log import logger
from request_data import request_data, get_fresh_copy


# Using the observer pattern to keep the derived views in sync with the
# dependent cache
class Observer:
    def __init__(self, observers_key, refresh_method):
        self.key = observers_key
        self.refresh = refresh_method


# Reverse observer pattern to refresh the dependent cache, in cases where the
# Observer has been requested and is stale. I call it the Actor pattern.
class Actor:
    def __init__(self, actors_key):
        self.key = actors_key


# The class attributes assumes that the clock skew will never exceed 10 seconds
# You may add other attributes such as the frequency, timestamp of the last access,
# etc. to implement different cache eviction strategies.
class Attributes:
    def __init__(self):
        self.observers = []
        self.actor = Actor('')
        self.expiry = datetime.now() + timedelta(seconds=-10)
        self.refreshed = False


# A simple basic cache which caches only a select set of keys and never evicts any
# key. This
class Cache:
    def __init__(self):
        self.cache = {}

    def add_observer(self, actors_key, observer):
        if actors_key in self.cache:
            [old_val, attributes] = self.cache[actors_key]
            attributes.observers.append(observer)
        else:
            raise KeyMissingFromCacheException(actors_key)

        if observer.key in self.cache:
            [old_val, attributes] = self.cache[observer.key]
            attributes.actor.key = actors_key
        else:
            raise KeyMissingFromCacheException(observer.key)

    def put(self, key, new_val, time_to_expiry_seconds):
        old_val = ''
        attributes = Attributes()

        # Only while registering the keys in the cache, time_to_expiry_seconds
        # is less than zero.
        if time_to_expiry_seconds >= 0:
            attributes.refreshed = True

        if key in self.cache:
            [old_val, attributes] = self.cache[key]
            attributes.refreshed = True
            attributes.expiry = datetime.now() + timedelta(seconds=time_to_expiry_seconds)
            self.cache[key] = [new_val, attributes]
        else:
            self.cache[key] = [new_val, attributes]

        for observer in attributes.observers:
            logger.debug('calling observer for %s, refreshed %s', observer.key, str(attributes.refreshed))
            [observer_old_val, observer_attributes] = self.cache[observer.key]
            observer_attributes.expiry = attributes.expiry
            observer_attributes.refreshed = attributes.refreshed
            if old_val != new_val:
                observer_new_val = observer.refresh(new_val)
            else:
                observer_new_val = observer_old_val
            self.cache[observer.key] = [observer_new_val, observer_attributes]

    def get(self, key):
        logger.debug('Getting %s', key)
        if key in self.cache:
            logger.debug('Cache hit for %s', key)
            [old_val, attributes] = self.cache[key]

            if attributes.expiry < datetime.now():
                logger.debug('Stale cache for %s', key)

                # If this cache of an observer is stale, we must
                # refresh the actor.
                query_key = key
                if attributes.actor.key:
                    query_key = attributes.actor.key

                # update the cache only if the copy is fresh
                [status_code, value] = get_fresh_copy(query_key)
                logger.debug('status code for get_fresh_copy %d', status_code)

                if status_code == 200:
                    self.put(query_key, value, app_config.max_time_to_expiry_seconds)

                [value, attributes] = self.cache[key]

                logger.debug('attributes.refreshed = %s', str(attributes.refreshed))

                # If the request failed, should we return what we have? Only if we were
                # able to refresh the value for the key at least once.
                if status_code != 200 and attributes.refreshed:
                    logger.debug('Request failed. Returning stale entry')
                    status_code = 200

                return [status_code, value]

            else:
                logger.debug('Fresh cache for %s', key)
                return [200, old_val]

        else:
            logger.debug('Cache miss for %s', key)
            return request_data(app_config.golden_source, key, app_config.leader_timeout)
