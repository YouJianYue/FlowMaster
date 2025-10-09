# -*- coding: utf-8 -*-
"""
字典服务实现
一比一复刻参考项目 DictServiceImpl.java

@author: FlowMaster
@since: 2025/10/04
"""

from typing import List, Optional
from sqlalchemy import select
from apps.system.core.service.dict_service import DictService
from apps.system.core.model.query.dict_query import DictQuery
from apps.system.core.model.req.dict_req import DictReq
from apps.system.core.model.resp.dict_resp import DictResp
from apps.system.core.model.entity.dict_entity import DictEntity
from apps.common.config.database.database_session import DatabaseSession
from apps.common.config.logging import get_logger
from apps.common.config.exception.global_exception_handler import BusinessException
from apps.common.context.user_context_holder import UserContextHolder

logger = get_logger(__name__)


class DictServiceImpl(DictService):
    """
    字典服务实现
    一比一复刻参考项目 DictServiceImpl (extends BaseServiceImpl)
    """

    async def list(self, query: DictQuery) -> List[DictResp]:
        """
        查询字典列表
        一比一复刻参考项目 DictServiceImpl.list()
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                stmt = select(DictEntity)

                # 关键词搜索（搜索名称、编码、描述）
                if query.description:
                    search_pattern = f"%{query.description}%"
                    stmt = stmt.where(
                        (DictEntity.name.like(search_pattern)) |
                        (DictEntity.code.like(search_pattern)) |
                        (DictEntity.description.like(search_pattern))
                    )

                # 按创建时间倒序
                stmt = stmt.order_by(DictEntity.create_time.desc())

                result = await session.execute(stmt)
                entities = result.scalars().all()

                # 转换为响应对象
                return [
                    DictResp(
                        id=entity.id,
                        name=entity.name,
                        code=entity.code,
                        description=entity.description,
                        is_system=entity.is_system,
                        create_user_string=str(entity.create_user) if entity.create_user else None,
                        create_time=entity.create_time,
                        update_user_string=str(entity.update_user) if entity.update_user else None,
                        update_time=entity.update_time
                    )
                    for entity in entities
                ]

        except Exception as e:
            logger.error(f"查询字典列表失败: {e}", exc_info=True)
            raise BusinessException(f"查询字典列表失败: {str(e)}")

    async def get(self, dict_id: int) -> DictResp:
        """
        查询字典详情
        一比一复刻参考项目 DictServiceImpl.get()
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                stmt = select(DictEntity).where(DictEntity.id == dict_id)
                result = await session.execute(stmt)
                entity = result.scalar_one_or_none()

                if entity is None:
                    raise BusinessException(f"字典不存在 [ID: {dict_id}]")

                return DictResp(
                    id=entity.id,
                    name=entity.name,
                    code=entity.code,
                    description=entity.description,
                    is_system=entity.is_system,
                    create_user_string=str(entity.create_user) if entity.create_user else None,
                    create_time=entity.create_time,
                    update_user_string=str(entity.update_user) if entity.update_user else None,
                    update_time=entity.update_time
                )

        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"查询字典详情失败 [ID: {dict_id}]: {e}", exc_info=True)
            raise BusinessException(f"查询字典详情失败: {str(e)}")

    async def create(self, req: DictReq) -> int:
        """
        创建字典

        一比一复刻参考项目逻辑:
        1. beforeCreate: 检查名称重复、检查编码重复
        2. 保存到数据库
        3. 返回ID
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 获取当前用户ID
                current_user_id = UserContextHolder.get_user_id()
                if current_user_id is None:
                    current_user_id = 1  # 如果未登录，默认使用1（超级管理员）

                # 1. beforeCreate: 检查名称和编码重复
                await self._check_name_repeat(req.name, session=session)
                await self._check_code_repeat(req.code, session=session)

                # 2. 创建实体
                entity = DictEntity(
                    name=req.name,
                    code=req.code,
                    description=req.description,
                    is_system=False,  # 新创建的都不是系统内置
                    create_user=current_user_id
                )

                session.add(entity)
                await session.flush()  # 获取自增ID

                logger.info(f"创建字典成功 [ID: {entity.id}, 名称: {req.name}, 编码: {req.code}]")
                return entity.id

        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"创建字典失败 [名称: {req.name}]: {e}", exc_info=True)
            raise BusinessException(f"创建字典失败: {str(e)}")

    async def update(self, dict_id: int, req: DictReq) -> None:
        """
        更新字典

        一比一复刻参考项目逻辑:
        1. beforeUpdate: 检查名称重复、不允许修改编码
        2. 更新数据库
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 获取当前用户ID
                current_user_id = UserContextHolder.get_user_id()
                if current_user_id is None:
                    current_user_id = 1  # 如果未登录，默认使用1（超级管理员）

                # 查询字典
                stmt = select(DictEntity).where(DictEntity.id == dict_id)
                result = await session.execute(stmt)
                entity = result.scalar_one_or_none()

                if entity is None:
                    raise BusinessException(f"字典不存在 [ID: {dict_id}]")

                # 1. beforeUpdate: 检查系统内置
                if entity.is_system:
                    raise BusinessException("系统内置数据不允许修改")

                # 2. 检查名称重复（排除自身）
                await self._check_name_repeat(req.name, dict_id=dict_id, session=session)

                # 3. 不允许修改编码（参考项目逻辑）
                if entity.code != req.code:
                    raise BusinessException("不允许修改字典编码")

                # 4. 更新字段
                entity.name = req.name
                entity.description = req.description
                entity.update_user = current_user_id

                await session.flush()

                logger.info(f"更新字典成功 [ID: {dict_id}, 名称: {req.name}]")

        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"更新字典失败 [ID: {dict_id}]: {e}", exc_info=True)
            raise BusinessException(f"更新字典失败: {str(e)}")

    async def batch_delete(self, ids: List[int]) -> None:
        """
        批量删除字典

        一比一复刻参考项目逻辑:
        1. beforeDelete: 检查是否为系统内置、级联删除字典项
        2. 删除数据库记录
        """
        try:
            from apps.system.core.service.dict_item_service import get_dict_item_service

            async with DatabaseSession.get_session_context() as session:
                # 查询要删除的字典
                stmt = select(DictEntity).where(DictEntity.id.in_(ids))
                result = await session.execute(stmt)
                entities = result.scalars().all()

                if not entities:
                    raise BusinessException("未找到要删除的字典")

                # 1. beforeDelete: 检查系统内置
                for entity in entities:
                    if entity.is_system:
                        raise BusinessException(f"系统内置数据不允许删除 [{entity.name}]")

                # 2. 级联删除字典项
                dict_item_service = get_dict_item_service()
                await dict_item_service.delete_by_dict_ids(ids)

                # 3. 删除字典
                for entity in entities:
                    await session.delete(entity)

                await session.flush()

                logger.info(f"批量删除字典成功 [IDs: {ids}]")

        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"批量删除字典失败 [IDs: {ids}]: {e}", exc_info=True)
            raise BusinessException(f"批量删除字典失败: {str(e)}")

    async def list_enum_dict(self) -> List[dict]:
        """
        查询枚举字典列表
        一比一复刻参考项目 DictServiceImpl.listEnumDict()

        返回格式: [{"label": "枚举名称", "value": "枚举编码"}, ...]
        """
        try:
            from apps.system.core.service.dict_item_service import get_dict_item_service

            dict_item_service = get_dict_item_service()
            enum_names = dict_item_service.list_enum_dict_names()

            # 转换为前端需要的格式（label-value格式）
            return [
                {"label": name, "value": name}
                for name in enum_names
            ]

        except Exception as e:
            logger.error(f"查询枚举字典列表失败: {e}", exc_info=True)
            raise BusinessException(f"查询枚举字典列表失败: {str(e)}")

    # ==================== 私有方法 ====================

    async def _check_name_repeat(self, name: str, dict_id: Optional[int] = None, session=None) -> None:
        """
        检查名称是否重复

        Args:
            name: 字典名称
            dict_id: 字典ID（更新时传入，排除自身）
            session: 数据库会话（可选，如果没有则创建新会话）
        """
        async def _do_check(db_session):
            stmt = select(DictEntity).where(DictEntity.name == name)

            # 更新时排除自身
            if dict_id is not None:
                stmt = stmt.where(DictEntity.id != dict_id)

            result = await db_session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                raise BusinessException(f"字典名称已存在: {name}")

        # 如果提供了session，直接使用；否则创建新会话
        if session:
            await _do_check(session)
        else:
            async with DatabaseSession.get_session_context() as new_session:
                await _do_check(new_session)

    async def _check_code_repeat(self, code: str, dict_id: Optional[int] = None, session=None) -> None:
        """
        检查编码是否重复

        Args:
            code: 字典编码
            dict_id: 字典ID（更新时传入，排除自身）
            session: 数据库会话（可选，如果没有则创建新会话）
        """
        async def _do_check(db_session):
            stmt = select(DictEntity).where(DictEntity.code == code)

            # 更新时排除自身
            if dict_id is not None:
                stmt = stmt.where(DictEntity.id != dict_id)

            result = await db_session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                raise BusinessException(f"字典编码已存在: {code}")

        # 如果提供了session，直接使用；否则创建新会话
        if session:
            await _do_check(session)
        else:
            async with DatabaseSession.get_session_context() as new_session:
                await _do_check(new_session)


# 依赖注入函数
def get_dict_service() -> DictService:
    """获取字典服务实例"""
    return DictServiceImpl()
