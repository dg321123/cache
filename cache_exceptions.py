class KeyMissingFromCacheException(Exception):
    def __init__(self, key):
        self.key = key

    def __str__(self):
        return repr(self.key)
