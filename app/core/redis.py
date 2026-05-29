"""
Redis 配置
"""
import json
from typing import Optional

import redis.asyncio as redis

from app.core.config import settings

# Redis 客户端
redis_client: Optional[redis.Redis] = None


async def init_redis():
    """初始化 Redis 连接"""
    global redis_client
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
        db=settings.REDIS_DB,
        decode_responses=True,
    )
    # 测试连接
    await redis_client.ping()


async def close_redis():
    """关闭 Redis 连接"""
    global redis_client
    if redis_client:
        await redis_client.close()


def get_redis() -> redis.Redis:
    """获取 Redis 客户端"""
    return redis_client


class RedisKeys:
    """Redis Key 命名规范"""

    # Token 相关
    ACCESS_TOKEN = "token:access:{user_id}"  # 用户 Access Token
    REFRESH_TOKEN = "token:refresh:{user_id}"  # 用户 Refresh Token
    TOKEN_BLACKLIST = "token:blacklist:{token}"  # Token 黑名单

    # 缓存相关
    USER_INFO = "cache:user:{user_id}"  # 用户信息缓存
    SHOP_FOODS = "cache:shop_foods:{shop_id}"  # 店铺食品缓存
    NEARBY_FOODS = "cache:nearby_foods:{lat}:{lng}"  # 附近食品缓存

    # 积分相关
    USER_POINTS = "points:user:{user_id}"  # 用户积分

    # 限流相关
    RATE_LIMIT = "ratelimit:{ip}:{endpoint}"  # 接口限流

    # 验证码
    SMS_CODE = "sms:code:{phone}"  # 短信验证码

    @classmethod
    def format(cls, key: str, **kwargs) -> str:
        """格式化 Key"""
        return key.format(**kwargs)

import string

class RedisHelper:
    """Redis 操作辅助类"""

    @staticmethod
    async def get(key: str) -> Optional[str]:
        """获取值"""
        return await redis_client.get(key)

    @staticmethod
    async def set(key: str, value: str, expire: int = None) -> bool:
        """设置值"""
        return await redis_client.set(key, value, ex=expire)

    @staticmethod
    async def delete(key: str) -> int:
        """删除键"""
        return await redis_client.delete(key)

    @staticmethod
    async def get_json(key: str) -> Optional[dict]:
        """获取 JSON"""
        data = await redis_client.get(key)
        if data:
            return json.loads(data)
        return None

    @staticmethod
    async def set_json(key: str, data: dict, expire: int = None) -> bool:
        """设置 JSON"""
        return await redis_client.set(key, json.dumps(data, ensure_ascii=False), ex=expire)

    @staticmethod
    async def incr(key: str, amount: int = 1) -> int:
        """递增"""
        return await redis_client.incrby(key, amount)

    @staticmethod
    async def decr(key: string, amount: int = 1) -> int:
        """递减"""
        return await redis_client.decrby(key, amount)
