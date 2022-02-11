from redis import Redis

from config import Config

cache = Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)


def make_cache_key(*args) -> str:
    return Config.REDIS_PREFIX.format(":".join(map(str, args)))
