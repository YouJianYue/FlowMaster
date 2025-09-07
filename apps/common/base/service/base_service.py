# -*- coding: utf-8 -*-

"""
业务接口基类

根据实际项目需要，自行重写 CRUD 接口或增加自定义通用业务方法

@param L: 列表类型
@param D: 详情类型  
@param Q: 查询条件类型
@param C: 创建或修改请求参数类型

"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel

# 泛型类型定义
L = TypeVar('L', bound=BaseModel)  # 列表类型
D = TypeVar('D', bound=BaseModel)  # 详情类型
Q = TypeVar('Q', bound=BaseModel)  # 查询条件类型
C = TypeVar('C', bound=BaseModel)  # 创建或修改请求参数类型


class BaseService(Generic[L, D, Q, C], ABC):
    """业务接口基类"""

    @abstractmethod
    async def page(self, query: Q, page: int = 1, size: int = 10) -> dict:
        """分页查询"""
        pass

    @abstractmethod
    async def list(self, query: Q) -> List[L]:
        """列表查询"""
        pass

    @abstractmethod
    async def get(self, entity_id: int) -> Optional[D]:
        """根据ID查询详情"""
        pass

    @abstractmethod
    async def create(self, create_req: C) -> int:
        """创建"""
        pass

    @abstractmethod
    async def update(self, entity_id: int, update_req: C) -> None:
        """修改"""
        pass

    @abstractmethod
    async def delete(self, entity_id: int) -> None:
        """删除"""
        pass

    @abstractmethod
    async def batch_delete(self, ids: List[int]) -> None:
        """批量删除"""
        pass
