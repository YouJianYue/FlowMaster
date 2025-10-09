# -*- coding: utf-8 -*-
"""
Redis工具类

一比一复刻参考项目 RedisUtils.java
提供Redis缓存操作的统一接口

@author: FlowMaster
@since: 2025/9/20
"""

import json
from typing import Optional, Any, List
from redis import asyncio as aioredis
from apps.common.config.logging.logging_config import get_logger

logger = get_logger(__name__)


class RedisUtils:
    """
    Redis工具类

    一比一复刻参考项目 RedisUtils.java
    提供异步Redis操作方法
    """

    _redis_client: Optional[aioredis.Redis] = None

    @classmethod
    async def get_client(cls) -> aioredis.Redis:
        """
        获取Redis客户端（单例模式）

        Returns:
            aioredis.Redis: Redis客户端实例
        """
        if cls._redis_client is None:
            from apps.common.config.redis_config import get_redis_config

            # 从配置类读取Redis配置
            redis_config = get_redis_config()

            try:
                cls._redis_client = await aioredis.from_url(
                    redis_config.url,
                    password=redis_config.password,
                    encoding="utf-8",
                    decode_responses=True,
                    max_connections=redis_config.max_connections,
                    socket_timeout=redis_config.socket_timeout,
                    socket_connect_timeout=redis_config.socket_connect_timeout
                )
                logger.info(f"Redis连接成功: {redis_config.url.split('@')[-1] if '@' in redis_config.url else redis_config.url}")
            except Exception as e:
                logger.error(f"Redis连接失败: {e}", exc_info=True)
                raise

        return cls._redis_client

    @classmethod
    async def set(cls, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """
        设置缓存

        Args:
            key: 缓存键
            value: 缓存值（自动序列化为JSON）
            expire: 过期时间（秒），None表示永不过期

        Returns:
            bool: 是否设置成功
        """
        try:
            client = await cls.get_client()

            # 将Python对象序列化为JSON
            if not isinstance(value, str):
                value = json.dumps(value, ensure_ascii=False)

            if expire:
                await client.setex(key, expire, value)
            else:
                await client.set(key, value)

            return True
        except Exception as e:
            logger.error(f"Redis set失败 key={key}: {e}", exc_info=True)
            return False

    @classmethod
    async def get(cls, key: str) -> Optional[Any]:
        """
        获取缓存

        Args:
            key: 缓存键

        Returns:
            Optional[Any]: 缓存值（自动反序列化JSON），不存在返回None
        """
        try:
            client = await cls.get_client()
            value = await client.get(key)

            if value is None:
                return None

            # 尝试反序列化JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"Redis get失败 key={key}: {e}", exc_info=True)
            return None

    @classmethod
    async def delete(cls, key: str) -> bool:
        """
        删除缓存

        Args:
            key: 缓存键

        Returns:
            bool: 是否删除成功
        """
        try:
            client = await cls.get_client()
            await client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis delete失败 key={key}: {e}", exc_info=True)
            return False

    @classmethod
    async def delete_by_pattern(cls, pattern: str) -> int:
        """
        根据模式删除缓存（一比一复刻参考项目）

        Args:
            pattern: 匹配模式，例如 "ROLE_MENU:*"

        Returns:
            int: 删除的键数量
        """
        try:
            client = await cls.get_client()

            # 使用SCAN命令查找匹配的键（避免KEYS命令阻塞）
            deleted_count = 0
            async for key in client.scan_iter(match=pattern, count=100):
                await client.delete(key)
                deleted_count += 1

            logger.info(f"Redis删除模式匹配键 pattern={pattern}, count={deleted_count}")
            return deleted_count
        except Exception as e:
            logger.error(f"Redis deleteByPattern失败 pattern={pattern}: {e}", exc_info=True)
            return 0

    @classmethod
    async def exists(cls, key: str) -> bool:
        """
        检查键是否存在

        Args:
            key: 缓存键

        Returns:
            bool: 是否存在
        """
        try:
            client = await cls.get_client()
            return await client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis exists失败 key={key}: {e}", exc_info=True)
            return False

    @classmethod
    async def expire(cls, key: str, seconds: int) -> bool:
        """
        设置键的过期时间

        Args:
            key: 缓存键
            seconds: 过期时间（秒）

        Returns:
            bool: 是否设置成功
        """
        try:
            client = await cls.get_client()
            return await client.expire(key, seconds)
        except Exception as e:
            logger.error(f"Redis expire失败 key={key}: {e}", exc_info=True)
            return False

    @classmethod
    async def keys(cls, pattern: str) -> List[str]:
        """
        查找匹配的键列表

        Args:
            pattern: 匹配模式

        Returns:
            List[str]: 匹配的键列表
        """
        try:
            client = await cls.get_client()
            keys = []
            async for key in client.scan_iter(match=pattern, count=100):
                keys.append(key)
            return keys
        except Exception as e:
            logger.error(f"Redis keys失败 pattern={pattern}: {e}", exc_info=True)
            return []

    @classmethod
    async def close(cls):
        """关闭Redis连接"""
        if cls._redis_client:
            await cls._redis_client.close()
            cls._redis_client = None
            logger.info("Redis连接已关闭")

    @classmethod
    async def check_status(cls) -> dict:
        """
        检查Redis连接状态（不暴露密码）

        Returns:
            dict: Redis状态信息
        """
        from apps.common.config.redis_config import get_redis_config

        redis_config = get_redis_config()

        try:
            # 尝试连接Redis
            client = await cls.get_client()

            # 执行PING命令测试连接
            await client.ping()

            # 获取Redis信息
            info = await client.info()

            # 隐藏密码的URL
            safe_url = redis_config.url
            if '@' in safe_url:
                # 格式: redis://:password@host:port/db
                # 转换为: redis://***@host:port/db
                parts = safe_url.split('@')
                protocol_and_auth = parts[0]  # redis://:password
                host_and_rest = parts[1]      # host:port/db

                # 提取协议部分
                if '://' in protocol_and_auth:
                    protocol = protocol_and_auth.split('://')[0]
                    safe_url = f"{protocol}://***@{host_and_rest}"
                else:
                    safe_url = f"***@{host_and_rest}"

            return {
                "connection": True,
                "redis_url": safe_url,
                "redis_version": info.get("redis_version", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "unknown"),
                "uptime_in_days": info.get("uptime_in_days", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
            }

        except Exception as e:
            logger.error(f"Redis状态检查失败: {e}", exc_info=True)

            # 隐藏密码的错误信息
            safe_url = redis_config.url
            if '@' in safe_url:
                parts = safe_url.split('@')
                safe_url = f"***@{parts[1]}" if len(parts) > 1 else "***"

            return {
                "connection": False,
                "redis_url": safe_url,
                "error": str(e)
            }


# 缓存键常量定义（一比一复刻参考项目 CacheConstants.java）
class CacheConstants:
    """缓存键常量"""

    # 分隔符
    DELIMITER = ":"

    # 角色菜单缓存前缀 (对应 ROLE_MENU:roleId)
    ROLE_MENU_KEY_PREFIX = f"ROLE_MENU{DELIMITER}"

    # 用户权限缓存前缀 (对应 USER_PERMISSION:userId)
    USER_PERMISSION_KEY_PREFIX = f"USER_PERMISSION{DELIMITER}"

    # 字典缓存前缀
    DICT_KEY_PREFIX = f"DICT{DELIMITER}"

    @classmethod
    def get_role_menu_key(cls, role_id: int) -> str:
        """
        获取角色菜单缓存键

        Args:
            role_id: 角色ID

        Returns:
            str: 缓存键，例如 "ROLE_MENU:1"
        """
        return f"{cls.ROLE_MENU_KEY_PREFIX}{role_id}"

    @classmethod
    def get_user_permission_key(cls, user_id: int) -> str:
        """
        获取用户权限缓存键

        Args:
            user_id: 用户ID

        Returns:
            str: 缓存键，例如 "USER_PERMISSION:1"
        """
        return f"{cls.USER_PERMISSION_KEY_PREFIX}{user_id}"
