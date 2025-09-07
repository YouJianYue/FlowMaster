# -*- coding: utf-8 -*-

"""
业务实现基类
"""

from typing import List, Optional, Type, TypeVar, Generic, cast
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, Column
from apps.common.base.service.base_service import BaseService, L, D, Q, C
from apps.common.base.model.entity.base_entity import BaseEntity

# 数据库实体类型
Entity = TypeVar('Entity', bound=BaseEntity)


class BaseServiceImpl(BaseService[L, D, Q, C], Generic[L, D, Q, C, Entity]):
    """业务实现基类"""

    def __init__(self, db: Session, entity_class: Type[Entity],
                 list_resp_class: Type[L], detail_resp_class: Type[D]):
        self.db = db
        self.entity_class = entity_class
        self.list_resp_class = list_resp_class
        self.detail_resp_class = detail_resp_class

    async def page(self, query: Q, page: int = 1, size: int = 10) -> dict:
        """分页查询"""
        # 构建查询条件
        query_filters = self._build_query_filters(query)

        # 总记录数
        query_obj = self.db.query(self.entity_class)
        if query_filters:
            query_obj = query_obj.filter(and_(*query_filters))
        total = query_obj.count()

        # 分页数据
        offset = (page - 1) * size
        query_obj = self.db.query(self.entity_class)
        if query_filters:
            query_obj = query_obj.filter(and_(*query_filters))
        
        records = (query_obj
                   .order_by(desc(cast(Column, self.entity_class.create_time)))
                   .offset(offset)
                   .limit(size)
                   .all())

        # 转换为响应模型
        list_data = [self.list_resp_class.model_validate(record) for record in records]

        return {
            "records": list_data,
            "total": total,
            "current": page,
            "size": size,
            "pages": (total + size - 1) // size
        }

    async def list(self, query: Q) -> List[L]:
        """列表查询"""
        query_filters = self._build_query_filters(query)
        query_obj = self.db.query(self.entity_class)
        if query_filters:
            query_obj = query_obj.filter(and_(*query_filters))
        
        records = (query_obj
                   .order_by(desc(cast(Column, self.entity_class.create_time)))
                   .all())

        return [self.list_resp_class.model_validate(record) for record in records]

    async def get(self, entity_id: int) -> Optional[D]:
        """根据ID查询详情"""
        record = self.db.query(self.entity_class).filter(cast(Column, self.entity_class.id) == entity_id).first()
        if record:
            return self.detail_resp_class.model_validate(record)
        return None

    async def create(self, create_req: C) -> int:
        """创建"""
        # 转换为实体对象
        entity_data = create_req.model_dump(exclude_unset=True)
        entity = self.entity_class(**entity_data)

        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)

        return entity.id

    async def update(self, entity_id: int, update_req: C) -> None:
        """修改"""
        entity = self.db.query(self.entity_class).filter(cast(Column, self.entity_class.id) == entity_id).first()
        if not entity:
            raise ValueError(f"ID为 {entity_id} 的记录不存在")

        # 更新字段
        update_data = update_req.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        self.db.commit()

    async def delete(self, entity_id: int) -> None:
        """删除"""
        entity = self.db.query(self.entity_class).filter(cast(Column, self.entity_class.id) == entity_id).first()
        if not entity:
            raise ValueError(f"ID为 {entity_id} 的记录不存在")

        self.db.delete(entity)
        self.db.commit()

    async def batch_delete(self, ids: List[int]) -> None:
        """批量删除"""
        self.db.query(self.entity_class).filter(cast(Column, self.entity_class.id).in_(ids)).delete(synchronize_session=False)
        self.db.commit()

    def _build_query_filters(self, query: Q) -> List:
        """构建查询条件"""
        filters = []

        # 子类可以重写此方法来实现具体的查询条件构建
        # 这里提供默认的实现
        if hasattr(query, 'model_dump'):
            query_dict = query.model_dump(exclude_unset=True)
            for key, value in query_dict.items():
                if value is not None and hasattr(self.entity_class, key):
                    column = cast(Column, getattr(self.entity_class, key))
                    filters.append(column == value)

        return filters
