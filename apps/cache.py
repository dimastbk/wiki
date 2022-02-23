from redis import Redis

from config import config

cache = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)


def make_cache_key(*args) -> str:
    return config.REDIS_PREFIX.format(":".join(map(str, args)))
