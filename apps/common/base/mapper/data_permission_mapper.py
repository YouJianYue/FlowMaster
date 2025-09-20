# -*- coding: utf-8 -*-

"""
数据权限映射器基类

一比一复刻参考项目 DataPermissionMapper.java
提供数据权限控制的基础数据访问接口

@author: FlowMaster
@since: 2025/9/19
"""

from abc import ABC
from typing import Generic, TypeVar, List, Optional, Any, Dict, Union
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, and_
from sqlalchemy.sql import Select

# 泛型类型定义
T = TypeVar('T')  # 实体类型


class DataPermissionQueryWrapper:
    """
    查询条件包装器

    对应参考项目的 Wrapper<T> queryWrapper
    提供灵活的查询条件构建
    """

    def __init__(self):
        self.conditions = []
        self.order_by = []
        self.limit_count = None
        self.offset_count = None

    def eq(self, field: str, value: Any) -> 'DataPermissionQueryWrapper':
        """等于条件"""
        self.conditions.append((field, '=', value))
        return self

    def ne(self, field: str, value: Any) -> 'DataPermissionQueryWrapper':
        """不等于条件"""
        self.conditions.append((field, '!=', value))
        return self

    def like(self, field: str, value: str) -> 'DataPermissionQueryWrapper':
        """模糊查询条件"""
        self.conditions.append((field, 'like', f"%{value}%"))
        return self

    def in_(self, field: str, values: List[Any]) -> 'DataPermissionQueryWrapper':
        """IN条件"""
        self.conditions.append((field, 'in', values))
        return self

    def between(self, field: str, start: Any, end: Any) -> 'DataPermissionQueryWrapper':
        """BETWEEN条件"""
        self.conditions.append((field, 'between', (start, end)))
        return self

    def order_by_asc(self, field: str) -> 'DataPermissionQueryWrapper':
        """升序排序"""
        self.order_by.append((field, 'asc'))
        return self

    def order_by_desc(self, field: str) -> 'DataPermissionQueryWrapper':
        """降序排序"""
        self.order_by.append((field, 'desc'))
        return self

    def limit(self, count: int) -> 'DataPermissionQueryWrapper':
        """限制查询数量"""
        self.limit_count = count
        return self

    def offset(self, count: int) -> 'DataPermissionQueryWrapper':
        """设置偏移量"""
        self.offset_count = count
        return self


class PageQuery:
    """
    分页查询参数

    对应参考项目的 IPage<T> page
    """

    def __init__(self, page: int = 1, size: int = 10):
        self.page = page
        self.size = size
        self.total = 0

    @property
    def offset(self) -> int:
        """计算偏移量"""
        return (self.page - 1) * self.size


class DataPermissionDecorator:
    """
    数据权限装饰器

    对应参考项目的 @DataPermission 注解
    用于标记需要数据权限控制的方法
    """

    def __init__(self, enable: bool = True):
        self.enable = enable

    def __call__(self, func):
        """装饰器实现"""
        def wrapper(*args, **kwargs):
            # 在这里可以添加数据权限检查逻辑
            # 例如：根据用户角色过滤数据
            if self.enable:
                # TODO: 实现具体的数据权限过滤逻辑
                # 1. 获取当前用户上下文
                # 2. 根据用户部门/角色构建数据权限条件
                # 3. 将权限条件添加到查询中
                pass
            return func(*args, **kwargs)
        return wrapper


class DataPermissionMapper(Generic[T], ABC):
    """
    数据权限映射器基类

    一比一复刻参考项目 DataPermissionMapper.java
    提供带数据权限控制的基础数据访问方法

    Args:
        T: 实体类型
    """

    def __init__(self, session: Session, entity_class: type):
        """
        初始化映射器

        Args:
            session: SQLAlchemy会话
            entity_class: 实体类
        """
        self.session = session
        self.entity_class = entity_class

    @DataPermissionDecorator(enable=True)
    async def select_list(self, query_wrapper: Optional[DataPermissionQueryWrapper] = None) -> List[T]:
        """
        根据条件查询全部记录

        一比一复刻参考项目:
        @DataPermission
        @Override
        List<T> selectList(@Param(Constants.WRAPPER) Wrapper<T> queryWrapper);

        Args:
            query_wrapper: 查询条件包装器

        Returns:
            查询结果列表
        """
        # 构建基础查询
        stmt = select(self.entity_class)

        # 应用查询条件
        if query_wrapper:
            stmt = self._apply_conditions(stmt, query_wrapper)
            stmt = self._apply_ordering(stmt, query_wrapper)

            # 应用分页
            if query_wrapper.limit_count:
                stmt = stmt.limit(query_wrapper.limit_count)
            if query_wrapper.offset_count:
                stmt = stmt.offset(query_wrapper.offset_count)

        # 执行查询
        result = await self.session.execute(stmt)
        return result.scalars().all()

    @DataPermissionDecorator(enable=True)
    async def select_page(self, page: PageQuery,
                         query_wrapper: Optional[DataPermissionQueryWrapper] = None) -> Dict[str, Any]:
        """
        根据条件分页查询记录

        一比一复刻参考项目:
        @DataPermission
        @Override
        List<T> selectList(IPage<T> page, @Param(Constants.WRAPPER) Wrapper<T> queryWrapper);

        Args:
            page: 分页参数
            query_wrapper: 查询条件包装器

        Returns:
            分页查询结果
        """
        # 构建基础查询
        stmt = select(self.entity_class)

        # 应用查询条件
        if query_wrapper:
            stmt = self._apply_conditions(stmt, query_wrapper)
            stmt = self._apply_ordering(stmt, query_wrapper)

        # 查询总数
        count_stmt = select(self.entity_class).with_only_columns([self.entity_class.id.distinct().label('count')])
        if query_wrapper:
            count_stmt = self._apply_conditions(count_stmt, query_wrapper)

        total_result = await self.session.execute(count_stmt)
        total = len(total_result.fetchall())

        # 应用分页
        stmt = stmt.limit(page.size).offset(page.offset)

        # 执行查询
        result = await self.session.execute(stmt)
        records = result.scalars().all()

        return {
            'records': records,
            'total': total,
            'page': page.page,
            'size': page.size,
            'pages': (total + page.size - 1) // page.size  # 总页数
        }

    @DataPermissionDecorator(enable=True)
    async def delete_by_id(self, entity_id: Union[int, str]) -> int:
        """
        根据ID删除记录

        一比一复刻参考项目:
        @DataPermission
        @Override
        int deleteById(@Param("id") Serializable id);

        Args:
            entity_id: 实体ID

        Returns:
            删除的记录数
        """
        stmt = delete(self.entity_class).where(self.entity_class.id == entity_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount

    async def select_by_id(self, entity_id: Union[int, str]) -> Optional[T]:
        """
        根据ID查询单条记录

        Args:
            entity_id: 实体ID

        Returns:
            查询结果
        """
        stmt = select(self.entity_class).where(self.entity_class.id == entity_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    def _apply_conditions(self, stmt: Select, query_wrapper: DataPermissionQueryWrapper) -> Select:
        """
        应用查询条件

        Args:
            stmt: SQL查询语句
            query_wrapper: 查询条件包装器

        Returns:
            应用条件后的查询语句
        """
        for field, operator, value in query_wrapper.conditions:
            column = getattr(self.entity_class, field, None)
            if column is None:
                continue

            if operator == '=':
                stmt = stmt.where(column == value)
            elif operator == '!=':
                stmt = stmt.where(column != value)
            elif operator == 'like':
                stmt = stmt.where(column.like(value))
            elif operator == 'in':
                stmt = stmt.where(column.in_(value))
            elif operator == 'between':
                start, end = value
                stmt = stmt.where(and_(column >= start, column <= end))

        return stmt

    def _apply_ordering(self, stmt: Select, query_wrapper: DataPermissionQueryWrapper) -> Select:
        """
        应用排序条件

        Args:
            stmt: SQL查询语句
            query_wrapper: 查询条件包装器

        Returns:
            应用排序后的查询语句
        """
        for field, direction in query_wrapper.order_by:
            column = getattr(self.entity_class, field, None)
            if column is None:
                continue

            if direction == 'asc':
                stmt = stmt.order_by(column.asc())
            elif direction == 'desc':
                stmt = stmt.order_by(column.desc())

        return stmt


# 使用示例和工厂方法
def create_data_permission_mapper(session: Session, entity_class: type) -> DataPermissionMapper:
    """
    创建数据权限映射器实例

    Args:
        session: SQLAlchemy会话
        entity_class: 实体类

    Returns:
        映射器实例
    """
    class ConcreteDataPermissionMapper(DataPermissionMapper[entity_class]):
        pass

    return ConcreteDataPermissionMapper(session, entity_class)


# 数据权限枚举
class DataPermissionType:
    """
    数据权限类型枚举

    对应参考项目中可能的数据权限类型
    """
    ALL = "ALL"           # 全部数据权限
    DEPT = "DEPT"         # 部门数据权限
    DEPT_AND_SUB = "DEPT_AND_SUB"  # 部门及子部门数据权限
    SELF = "SELF"         # 仅本人数据权限
    CUSTOM = "CUSTOM"     # 自定义数据权限