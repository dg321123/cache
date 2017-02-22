from datetime import datetime, timedelta
from request_data import request_data

MAX_TIME_TO_EXPIRY_SECONDS = 2


class Observer:
    def __init__(self, key, refresh_method):
        self.key = key
        self.refresh = refresh_method


# The class attributes assumes that the clock skew will never exceed 10 seconds
class Attributes:
    def __init__(self):
        self.observers = []
        self.expiry = datetime.now() + timedelta(seconds=-10)


class Cache:
    def __init__(self):
        self.cache = {}
        self.backup_host = 'api.github.com'

    def add_observer(self, key, observer):
        if key in self.cache:
            [old_val, attributes] = self.cache[key]
            attributes.observers.append(observer)

    def put(self, key, new_val, time_to_expiry_seconds):
        old_val = ''
        attributes = Attributes()

        if key in self.cache:
            [old_val, attributes] = self.cache[key]
            attributes.expiry = datetime.now() + timedelta(seconds=time_to_expiry_seconds)
            self.cache[key] = [new_val, attributes]
        else:
            self.cache[key] = [new_val, attributes]

        if old_val != new_val:
            for observer in attributes.observers:
                print 'calling observer for ', observer.key
                [observer_old_val, observer_attributes] = self.cache[observer.key]
                observer_attributes.expiry = attributes.expiry
                observer_new_val = observer.refresh(new_val)
                self.cache[observer.key] = [observer_new_val, observer_attributes]

    def get(self, key):
        print 'Getting ', key
        if key in self.cache:
            print 'Cache hit'
            [old_val, attributes] = self.cache[key]

            if attributes.expiry < datetime.now():
                print 'Stale cache'
                value = []
                [status_code, value] = self.get_fresh_copy(key)
                if status_code == 200:
                    self.put(key, value, MAX_TIME_TO_EXPIRY_SECONDS)
                return [status_code, value]
            else:
                print 'Fresh cache'
                return [200, old_val]
        else:
            print 'Cache miss'
            return request_data(self.backup_host, key, value)

    # TODO implement leader lookup.
    def get_fresh_copy(self, key):
        return request_data(self.backup_host, key)


