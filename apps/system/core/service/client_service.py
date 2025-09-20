# -*- coding: utf-8 -*-

"""
客户端服务 - 对应参考项目的ClientService
"""

from typing import Optional, List
from sqlalchemy import select
from apps.system.core.model.entity.client_entity import ClientEntity
from apps.system.core.model.resp.client_resp import ClientResponse, ClientInfo
from apps.common.config.exception.global_exception_handler import BusinessException
from apps.common.config.database.database_session import DatabaseSession


class ClientService:
    """
    客户端业务服务

    对应Java服务: ClientService
    提供客户端验证、查询等核心功能
    """

    def __init__(self):
        """
        初始化客户端服务
        """
        pass

    async def get_by_client_id(self, client_id: str) -> Optional[ClientInfo]:
        """
        根据客户端ID查询客户端信息

        Args:
            client_id: 客户端ID

        Returns:
            Optional[ClientInfo]: 客户端信息，不存在则返回None
        """
        async with DatabaseSession.get_session_context() as session:
            stmt = select(ClientEntity).where(ClientEntity.client_id == client_id)
            result = await session.execute(stmt)
            client_entity = result.scalar_one_or_none()

            if client_entity is None:
                return None

            # 转换为ClientInfo
            return ClientInfo.model_validate(client_entity)

    async def validate_client(self, client_id: str, auth_type: str) -> ClientInfo:
        """
        验证客户端（完全对应参考项目的验证逻辑）

        Args:
            client_id: 客户端ID
            auth_type: 认证类型

        Returns:
            ClientInfo: 验证通过的客户端信息

        Raises:
            BusinessException: 客户端验证失败
        """
        # 1. 校验客户端是否存在
        client = await self.get_by_client_id(client_id)
        if client is None:
            raise BusinessException("客户端不存在")

        # 2. 校验客户端状态
        if not client.is_enabled():
            raise BusinessException("客户端已禁用")

        # 3. 校验认证类型授权
        if not client.is_auth_type_supported(auth_type):
            raise BusinessException(f"该客户端暂未授权 [{auth_type}] 认证")

        return client

    async def get_client_response(self, client_id: str) -> Optional[ClientResponse]:
        """
        获取客户端完整响应信息

        Args:
            client_id: 客户端ID

        Returns:
            Optional[ClientResponse]: 客户端响应信息
        """
        async with DatabaseSession.get_session_context() as session:
            stmt = select(ClientEntity).where(ClientEntity.client_id == client_id)
            result = await session.execute(stmt)
            client_entity = result.scalar_one_or_none()

            if client_entity is None:
                return None

            # 转换为ClientResponse
            return ClientResponse.model_validate(client_entity)

    async def list_all_clients(self) -> List[ClientResponse]:
        """
        获取所有客户端列表

        Returns:
            List[ClientResponse]: 客户端列表
        """
        async with DatabaseSession.get_session_context() as session:
            stmt = select(ClientEntity).order_by(ClientEntity.create_time.desc())
            result = await session.execute(stmt)
            client_entities = result.scalars().all()

            return [ClientResponse.model_validate(entity) for entity in client_entities]

    async def list_enabled_clients(self) -> List[ClientResponse]:
        """
        获取启用状态的客户端列表

        Returns:
            List[ClientResponse]: 启用的客户端列表
        """
        async with DatabaseSession.get_session_context() as session:
            stmt = (
                select(ClientEntity)
                .where(ClientEntity.status == 1)  # 启用状态
                .order_by(ClientEntity.create_time.desc())
            )
            result = await session.execute(stmt)
            client_entities = result.scalars().all()

            return [ClientResponse.model_validate(entity) for entity in client_entities]


# 依赖注入函数
def get_client_service() -> ClientService:
    """
    获取客户端服务实例（依赖注入）

    Returns:
        ClientService: 客户端服务实例
    """
    return ClientService()