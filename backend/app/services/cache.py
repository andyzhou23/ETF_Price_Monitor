import redis
import json
from ..config import settings
from typing import Any, Optional

class RedisCache:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)

    def get(self, key: str) -> Optional[Any]:
        try:
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            print("Redis get error:", e)
        return None

    def set(self, key: str, value: Any, ttl: int = 3600):
        try:
            self.redis_client.setex(key, ttl, json.dumps(value))
        except Exception as e:
            print("Redis set error:", e)

    def invalidate_etf(self, etf_id: int):
        keys = [
            f"etf:{etf_id}:constituents",
            f"etf:{etf_id}:price_history",
            f"etf:{etf_id}:top_holdings"
        ]
        try:
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            print("Redis invalidate error:", e)

redis_cache = RedisCache()
