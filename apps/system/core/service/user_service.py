# -*- coding: utf-8 -*-
"""
用户服务接口和实现
"""

from abc import ABC, abstractmethod
from typing import Optional, Union, List, TYPE_CHECKING
from sqlalchemy import select

from apps.system.core.model.resp.user_resp import UserResp
from apps.system.core.model.resp.user_detail_resp import UserDetailResp
from apps.common.models.page_resp import PageResp
from apps.common.config.database.database_session import DatabaseSession
from apps.system.core.model.entity.user_entity import UserEntity
from apps.common.config.logging import get_logger

if TYPE_CHECKING:
    pass

logger = get_logger(__name__)


class UserService(ABC):
    """用户服务接口"""

    @abstractmethod
    async def get_user_page(
        self,
        dept_id: Optional[Union[int, str]] = None,
        description: Optional[str] = None,
        status: Optional[int] = None,
        page: int = 1,
        size: int = 10,
        sort: Optional[str] = None
    ) -> PageResp[UserResp]:
        """
        分页查询用户列表

        Args:
            dept_id: 部门ID
            description: 关键词（搜索用户名、昵称等）
            status: 用户状态（1=启用，2=禁用）
            page: 页码
            size: 每页大小
            sort: 排序字段

        Returns:
            PageResp[UserResp]: 分页用户数据
        """
        pass

    @abstractmethod
    async def get_user_detail(self, user_id: Union[int, str]) -> UserDetailResp:
        """
        获取用户详情

        Args:
            user_id: 用户ID

        Returns:
            UserDetailResp: 用户详情数据
        """
        pass

    @abstractmethod
    async def get(self, user_id: Union[int, str]) -> Optional[UserEntity]:
        """
        根据ID获取用户实体

        Args:
            user_id: 用户ID

        Returns:
            Optional[UserEntity]: 用户实体
        """
        pass

    @abstractmethod
    async def delete(self, ids: List[Union[int, str]]):
        """
        批量删除用户

        Args:
            ids: 用户ID列表
        """
        pass


class UserServiceImpl(UserService):
    """用户服务实现类"""

    async def get_user_page(
        self,
        dept_id: Optional[Union[int, str]] = None,
        description: Optional[str] = None,
        status: Optional[int] = None,
        page: int = 1,
        size: int = 10,
        sort: Optional[str] = None
    ) -> PageResp[UserResp]:
        """分页查询用户列表"""
        # TODO: 实现用户分页查询
        return PageResp(total=0, items=[])

    async def get_user_detail(self, user_id: Union[int, str]) -> UserDetailResp:
        """获取用户详情"""
        # TODO: 实现用户详情查询
        pass

    async def get(self, user_id: Union[int, str]) -> Optional[UserEntity]:
        """根据ID获取用户实体"""
        async with DatabaseSession.get_session_context() as session:
            try:
                # 查询用户信息
                stmt = select(UserEntity).where(UserEntity.id == user_id)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()
                return user
            except Exception as e:
                logger.error(f"获取用户信息失败: {e}")
                return None


# 依赖注入函数
def get_user_service() -> UserService:
    """
    获取用户服务实例（依赖注入）

    Returns:
        UserService: 用户服务实例
    """
    from apps.system.core.service.impl.user_service_impl import UserServiceImpl
    return UserServiceImpl()