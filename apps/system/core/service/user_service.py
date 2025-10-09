# -*- coding: utf-8 -*-
"""
用户服务接口
"""

from abc import ABC, abstractmethod
from typing import Optional, Union

from apps.system.core.model.entity.user_entity import UserEntity
from apps.system.core.model.resp.user_resp import UserResp
from apps.system.core.model.resp.user_detail_resp import UserDetailResp
from apps.system.core.model.req.user_req import UserUpdateReq
from apps.system.core.model.req.user_role_update_req import UserRoleUpdateReq
from apps.common.models.page_resp import PageResp


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
    async def get(self, user_id: Union[int, str]) -> UserEntity:
        """
        根据用户ID获取用户实体

        Args:
            user_id: 用户ID

        Returns:
            UserEntity: 用户实体

        Raises:
            BusinessException: 当用户不存在时抛出异常
        """
        pass

    @abstractmethod
    async def update_user(self, user_id: Union[int, str], update_req: UserUpdateReq) -> None:
        """
        更新用户信息

        Args:
            user_id: 用户ID
            update_req: 用户更新请求
        """
        pass

    @abstractmethod
    async def update_role(self, update_req: UserRoleUpdateReq, user_id: Union[int, str]) -> None:
        """
        分配用户角色

        Args:
            update_req: 用户角色更新请求
            user_id: 用户ID
        """
        pass

    @abstractmethod
    async def get_user_dict(self, status: Optional[int] = None) -> list:
        """
        查询用户字典列表（用于下拉选择）

        Args:
            status: 用户状态（1=启用，2=禁用，None=全部）

        Returns:
            list: 用户字典列表 [{"label": "用户昵称", "value": 用户ID}, ...]
        """
        pass


# 依赖注入函数
def get_user_service() -> UserService:
    """
    获取用户服务实例（依赖注入）

    Returns:
        UserService: 用户服务实例
    """
    from apps.system.core.service.impl.user_service_impl import UserServiceImpl
    return UserServiceImpl()