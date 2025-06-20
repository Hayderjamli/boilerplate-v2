import redis
import os
from dotenv import load_dotenv

load_dotenv()

def get_redis():
    return redis.Redis(
        host=os.getenv("REDIS_HOST"),
        port=int(os.getenv("REDIS_PORT")),
        decode_responses=True
    )
