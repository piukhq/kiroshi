import socket

import pendulum
import redis
from loguru import logger

from kiroshi.settings import settings


def leader_election(job_name: str) -> bool:
    r = redis.Redis.from_url(settings.redis_dsn)
    lock_key = f"kiroshi-job-{job_name}"
    hostname = socket.gethostname()
    is_leader = False

    with r.pipeline() as pipe:
        try:
            pipe.watch(lock_key)
            leader_host = pipe.get(lock_key)
            if leader_host in (hostname.encode(), None):
                pipe.multi()
                pipe.setex(lock_key, pendulum.duration(minutes=3), hostname)
                pipe.execute()
                is_leader = True
        except redis.WatchError:
            pass
    if not is_leader:
        logger.warning("Leader Election Failed, exiting.")
    return is_leader
