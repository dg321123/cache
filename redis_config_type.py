# This class encapsulates the configuration for the Redis database where the leader record exists.
class RedisConfigType:
    def __init__(self, hostname, port, db):
        self.type = 'RedisConfig'
        self.hostname = hostname
        self.port = port
        self.db = db
