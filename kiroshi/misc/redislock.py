from kiroshi.settings import settings

from typing import Literal

import pendulum
import socket
from loguru import logger
import redis
import hashlib


class RedisLock():
    def __init__(self, lock_name: str, lock_data: str | None = None, lock_mins: int = 3):
        self.lock_name = lock_name
        self.lock_mins = lock_mins
        self.lock_data = lock_data

    def lock(self):
        r = redis.Redis.from_url(settings.redis_dsn)
        lock_key = f"kiroshi-{self.lock_name}"
        if self.lock_data:
            lock_data = hashlib.sha256(self.lock_data.encode()).hexdigest()
        else:
            lock_data = socket.gethostname()

        locked = False

        with r.pipeline() as pipe:
            try:
                pipe.watch(lock_key)
                redis_value = pipe.get(lock_key)
                if redis_value in (lock_data.encode(), None):
                    pipe.multi()
                    pipe.setex(lock_key, pendulum.duration(minutes=self.lock_mins), lock_data)
                    pipe.execute()
                    if self.lock_data and redis_value is not None:
                        locked = False
                    else:
                        locked = True
            except redis.WatchError:
                pass
        if not locked:
            logger.info(f"Locking Failed, Lock Name: {self.lock_name}")
        return locked
