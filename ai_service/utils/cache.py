from functools import lru_cache

@lru_cache(maxsize=1000)
def cache_response(key):
    return None

def save_cache(key, value):
    cache_response.cache_clear()
