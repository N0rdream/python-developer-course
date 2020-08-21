import redis
import time
import random
import json


class Store:

    def __init__(self, host, port, reconnect_max_attempts=5, reconnect_delay=0.1):
        self.rdb = redis.StrictRedis(host, port, db=0, decode_responses=True)
        self.reconnect_max_attempts = reconnect_max_attempts
        self.reconnect_delay = reconnect_delay

    def cache_set(self, key, score, cache_valid=60 * 60):
        attempts = 0
        while attempts < self.reconnect_max_attempts:
            try:
                value = {'score': score, 'cache_timestamp': int(time.time()) + cache_valid}
                self.rdb[key] = json.dumps(value)
            except redis.exceptions.ConnectionError:
                time.sleep(self.reconnect_delay)
                attempts += 1
            else:
                return False

    def cache_get(self, key):
        attempts = 0
        while attempts < self.reconnect_max_attempts:
            try:
                value = self.rdb.get(key)
            except redis.exceptions.ConnectionError:
                time.sleep(self.reconnect_delay)
                attempts += 1
            else:
                if value is None:
                    return 0
                cache = json.loads(value)
                if cache['cache_timestamp'] < time.time():
                    return 0
                return cache['score']

    def get(self, cid):
        value = self.rdb.get(cid)
        return value if value is not None else []
