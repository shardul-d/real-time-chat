from redis.asyncio import Redis

redis = Redis.from_url(  # pyright: ignore[reportUnknownMemberType]
    "redis://localhost:6379/0", encoding="utf-8", decode_response=True
)
