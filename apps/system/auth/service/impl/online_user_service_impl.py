# -*- coding: utf-8 -*-

"""
在线用户服务实现 - 一比一复刻OnlineUserServiceImpl
"""

import json
from typing import List, Optional
from datetime import datetime
from apps.system.auth.service.online_user_service import OnlineUserService
from apps.system.auth.model.query.online_user_query import OnlineUserQuery
from apps.system.auth.model.resp.online_user_resp import OnlineUserResp
from apps.common.models.page_query import PageQuery
from apps.common.models.page_resp import PageResp
from apps.common.util.redis_utils import RedisUtils
from apps.common.config.logging import get_logger

logger = get_logger(__name__)


class OnlineUserServiceImpl(OnlineUserService):
    """在线用户服务实现 - 一比一复刻参考项目"""

    # Token在Redis中的key前缀
    TOKEN_KEY_PREFIX = "online_user:"

    async def page(self, query: OnlineUserQuery, page_query: PageQuery) -> PageResp[OnlineUserResp]:
        """分页查询在线用户列表"""
        # 查询所有在线用户
        all_users = await self.list(query)

        # 手动分页
        start = (page_query.page - 1) * page_query.size
        end = start + page_query.size
        page_users = all_users[start:end]

        total = len(all_users)
        pages = (total + page_query.size - 1) // page_query.size if total > 0 else 0

        return PageResp(
            list=page_users,
            total=total,
            current=page_query.page,
            size=page_query.size,
            pages=pages
        )

    async def list(self, query: OnlineUserQuery) -> List[OnlineUserResp]:
        """
        查询在线用户列表 - 一比一复刻参考项目

        从Redis查询所有在线Token，解析用户信息，应用过滤条件
        """
        result = []

        try:
            # 查询所有在线用户的Token key
            pattern = f"{self.TOKEN_KEY_PREFIX}*"
            token_keys = await RedisUtils.keys(pattern)

            logger.info(f"查询到 {len(token_keys)} 个在线Token")

            for token_key in token_keys:
                # 从Redis获取用户信息
                user_data = await RedisUtils.get(token_key)
                if not user_data:
                    continue

                # 解析用户信息
                try:
                    if isinstance(user_data, str):
                        user_data = json.loads(user_data)

                    # 提取Token（去掉前缀）
                    token = token_key.replace(self.TOKEN_KEY_PREFIX, "")

                    # 应用过滤条件
                    if not self._match_query(user_data, query):
                        continue

                    # 构建响应对象
                    online_user = OnlineUserResp(
                        id=user_data.get("id"),
                        token=token,
                        username=user_data.get("username"),
                        nickname=user_data.get("nickname"),
                        client_type=user_data.get("client_type"),
                        client_id=user_data.get("client_id"),
                        ip=user_data.get("ip"),
                        address=user_data.get("address"),
                        browser=user_data.get("browser"),
                        os=user_data.get("os"),
                        login_time=datetime.fromisoformat(user_data.get("login_time")),
                        last_active_time=datetime.fromisoformat(user_data.get("last_active_time")) if user_data.get("last_active_time") else None
                    )
                    result.append(online_user)

                except (json.JSONDecodeError, ValueError, TypeError) as e:
                    logger.warning(f"解析在线用户数据失败: {e}")
                    continue

            # 按登录时间倒序排序
            result.sort(key=lambda x: x.login_time, reverse=True)

        except Exception as e:
            logger.error(f"查询在线用户列表失败: {e}", exc_info=True)

        return result

    async def get_last_active_time(self, token: str) -> Optional[datetime]:
        """查询Token最后活跃时间"""
        try:
            token_key = f"{self.TOKEN_KEY_PREFIX}{token}"
            user_data = await RedisUtils.get(token_key)

            if user_data:
                if isinstance(user_data, str):
                    user_data = json.loads(user_data)
                last_active_time_str = user_data.get("last_active_time")
                if last_active_time_str:
                    return datetime.fromisoformat(last_active_time_str)

        except Exception as e:
            logger.error(f"查询最后活跃时间失败: {e}")

        return None

    async def kickout(self, token: str) -> None:
        """强退用户 - 删除Redis中的Token"""
        try:
            token_key = f"{self.TOKEN_KEY_PREFIX}{token}"
            await RedisUtils.delete(token_key)
            logger.info(f"强退用户成功: token={token[:20]}...")
        except Exception as e:
            logger.error(f"强退用户失败: {e}", exc_info=True)
            raise

    def _match_query(self, user_data: dict, query: OnlineUserQuery) -> bool:
        """
        匹配查询条件 - 一比一复刻参考项目的过滤逻辑

        Args:
            user_data: 用户数据
            query: 查询条件

        Returns:
            bool: 是否匹配
        """
        # 昵称/用户名过滤
        if query.nickname:
            username = user_data.get("username", "")
            nickname = user_data.get("nickname", "")
            if query.nickname.lower() not in username.lower() and query.nickname.lower() not in nickname.lower():
                return False

        # 客户端ID过滤
        if query.client_id:
            if user_data.get("client_id") != query.client_id:
                return False

        # 登录时间范围过滤
        if query.login_time and len(query.login_time) == 2:
            try:
                login_time = datetime.fromisoformat(user_data.get("login_time"))
                if not (query.login_time[0] <= login_time <= query.login_time[1]):
                    return False
            except (ValueError, TypeError):
                return False

        return True


def get_online_user_service() -> OnlineUserService:
    """获取在线用户服务实例"""
    return OnlineUserServiceImpl()
