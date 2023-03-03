from kiroshi.settings import settings
import redis
import hashlib
import pendulum
from loguru import logger


def alert_suppression(alert_name: str, alert_value: str, duration_mins: int = 60) -> bool:
    r = redis.Redis.from_url(settings.redis_dsn)
    lock_key = f"kiroshi-alert-{alert_name}"
    alert_sha = hashlib.sha256(alert_value.encode()).hexdigest()
    fire_alert = False

    with r.pipeline() as pipe:
        try:
            pipe.watch(lock_key)
            pipe_value = pipe.get(lock_key)
            if pipe_value in (alert_sha, None):
                pipe.multi()
                pipe.setex(lock_key, pendulum.duration(minutes=duration_mins), alert_sha)
                pipe.execute()
                fire_alert = True
        except redis.WatchError:
            pass
    if not fire_alert:
        logger.info("Alert Suppressed")
    return fire_alert
