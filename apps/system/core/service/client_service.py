# -*- coding: utf-8 -*-

"""
客户端服务 - 对应参考项目的ClientService
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import Depends
from apps.system.core.model.entity.client_entity import ClientEntity
from apps.system.core.model.resp.client_resp import ClientResponse, ClientInfo
from apps.system.core.model.data.default_clients import CLIENT_DATA_DICT
from apps.common.config.exception.global_exception_handler import BusinessException
from apps.common.enums.dis_enable_status_enum import DisEnableStatusEnum


class ClientService:
    """
    客户端业务服务
    
    对应Java服务: ClientService
    提供客户端验证、查询等核心功能
    """
    
    def __init__(self, db_session: Optional[Session]):
        """
        初始化客户端服务
        
        Args:
            db_session: 数据库会话（可选，为None时使用默认测试数据）
        """
        self.db = db_session
    
    async def get_by_client_id(self, client_id: str) -> Optional[ClientInfo]:
        """
        根据客户端ID查询客户端信息
        
        Args:
            client_id: 客户端ID
            
        Returns:
            Optional[ClientInfo]: 客户端信息，不存在则返回None
        """
        # 如果有数据库会话，从数据库查询
        if self.db is not None:
            stmt = select(ClientEntity).where(ClientEntity.client_id == client_id)
            result = self.db.execute(stmt)
            client_entity = result.scalar_one_or_none()
            
            if client_entity is None:
                return None
            
            # 转换为ClientInfo
            return ClientInfo.model_validate(client_entity)
        
        # 否则使用默认测试数据
        client_entity = CLIENT_DATA_DICT.get(client_id)
        if client_entity is None:
            return None
        
        # 转换为ClientInfo
        return ClientInfo(
            client_id=client_entity.client_id,
            client_type=client_entity.client_type,
            auth_type=client_entity.auth_type,
            active_timeout=client_entity.active_timeout,
            timeout=client_entity.timeout,
            status=client_entity.status
        )
    
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
        # 如果有数据库会话，从数据库查询
        if self.db is not None:
            stmt = select(ClientEntity).where(ClientEntity.client_id == client_id)
            result = self.db.execute(stmt)
            client_entity = result.scalar_one_or_none()
            
            if client_entity is None:
                return None
            
            # 转换为ClientResponse
            return ClientResponse.model_validate(client_entity)
        
        # 否则使用默认测试数据
        client_entity = CLIENT_DATA_DICT.get(client_id)
        if client_entity is None:
            return None
        
        # 手动构造ClientResponse
        return ClientResponse(
            id=client_entity.id,
            client_id=client_entity.client_id,
            client_type=client_entity.client_type,
            auth_type=client_entity.auth_type,
            active_timeout=client_entity.active_timeout,
            timeout=client_entity.timeout,
            status=client_entity.status,
            create_time=client_entity.create_time,
            create_user=client_entity.create_user,
            update_time=client_entity.update_time,
            update_user=client_entity.update_user
        )
    
    async def list_all_clients(self) -> List[ClientResponse]:
        """
        获取所有客户端列表
        
        Returns:
            List[ClientResponse]: 客户端列表
        """
        if self.db is not None:
            stmt = select(ClientEntity).order_by(ClientEntity.create_time.desc())
            result = self.db.execute(stmt)
            client_entities = result.scalars().all()
            
            return [ClientResponse.model_validate(entity) for entity in client_entities]
        
        # 使用默认测试数据
        return [
            ClientResponse(
                id=entity.id,
                client_id=entity.client_id,
                client_type=entity.client_type,
                auth_type=entity.auth_type,
                active_timeout=entity.active_timeout,
                timeout=entity.timeout,
                status=entity.status,
                create_time=entity.create_time,
                create_user=entity.create_user,
                update_time=entity.update_time,
                update_user=entity.update_user
            )
            for entity in CLIENT_DATA_DICT.values()
        ]
    
    async def list_enabled_clients(self) -> List[ClientResponse]:
        """
        获取启用状态的客户端列表
        
        Returns:
            List[ClientResponse]: 启用的客户端列表
        """
        if self.db is not None:
            stmt = select(ClientEntity).where(
                ClientEntity.status == DisEnableStatusEnum.ENABLE.value
            ).order_by(ClientEntity.create_time.desc())
            result = self.db.execute(stmt)
            client_entities = result.scalars().all()
            
            return [ClientResponse.model_validate(entity) for entity in client_entities]
        
        # 使用默认测试数据，过滤启用状态
        enabled_clients = [
            entity for entity in CLIENT_DATA_DICT.values() 
            if entity.status == DisEnableStatusEnum.ENABLE
        ]
        
        return [
            ClientResponse(
                id=entity.id,
                client_id=entity.client_id,
                client_type=entity.client_type,
                auth_type=entity.auth_type,
                active_timeout=entity.active_timeout,
                timeout=entity.timeout,
                status=entity.status,
                create_time=entity.create_time,
                create_user=entity.create_user,
                update_time=entity.update_time,
                update_user=entity.update_user
            )
            for entity in enabled_clients
        ]


# 依赖注入函数
def get_client_service(db_session: Optional[Session] = None) -> ClientService:
    """
    获取客户端服务实例（依赖注入）
    
    Args:
        db_session: 数据库会话
        
    Returns:
        ClientService: 客户端服务实例
    """
    return ClientService(db_session)