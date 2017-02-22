from datetime import datetime, timedelta
from request_data import request_data

MAX_TIME_TO_EXPIRY_SECONDS = 10


class Observer:
    def __init__(self, observers_key, refresh_method):
        self.key = observers_key
        self.refresh = refresh_method


class Actor:
    def __init__(self, actors_key):
        self.key = actors_key


# The class attributes assumes that the clock skew will never exceed 10 seconds
class Attributes:
    def __init__(self):
        self.observers = []
        self.actor = Actor('')
        self.expiry = datetime.now() + timedelta(seconds=-10)


class Cache:
    def __init__(self):
        self.cache = {}
        self.backup_host = 'api.github.com'

    def add_observer(self, actors_key, observer):
        if actors_key in self.cache:
            [old_val, attributes] = self.cache[actors_key]
            attributes.observers.append(observer)
        if observer.key in self.cache:
            [old_val, attributes] = self.cache[observer.key]
            attributes.actor.key = actors_key

    def put(self, key, new_val, time_to_expiry_seconds):
        old_val = ''
        attributes = Attributes()

        if key in self.cache:
            [old_val, attributes] = self.cache[key]
            attributes.expiry = datetime.now() + timedelta(seconds=time_to_expiry_seconds)
            self.cache[key] = [new_val, attributes]
        else:
            self.cache[key] = [new_val, attributes]

        for observer in attributes.observers:
            print 'calling observer for ', observer.key
            [observer_old_val, observer_attributes] = self.cache[observer.key]
            observer_attributes.expiry = attributes.expiry
            if old_val != new_val:
                observer_new_val = observer.refresh(new_val)
            else:
                observer_new_val = observer_old_val
            self.cache[observer.key] = [observer_new_val, observer_attributes]

    def get(self, key):
        print 'Getting ', key
        if key in self.cache:
            print 'Cache hit'
            [old_val, attributes] = self.cache[key]

            if attributes.expiry < datetime.now():
                print 'Stale cache'

                # If this cache of an observer is stale, we must
                # refresh the actor.
                query_key = key
                if attributes.actor.key:
                    query_key = attributes.actor.key

                value = []
                [status_code, value] = self.get_fresh_copy(query_key)
                if status_code == 200:
                    self.put(query_key, value, MAX_TIME_TO_EXPIRY_SECONDS)

                if attributes.actor.key:
                    [value, attributes] = self.cache[key]

                return [status_code, value]

            else:
                print 'Fresh cache'
                return [200, old_val]

        else:
            print 'Cache miss'
            return request_data(self.backup_host, key)

    # TODO implement leader lookup.
    def get_fresh_copy(self, key):
        return request_data(self.backup_host, key)


