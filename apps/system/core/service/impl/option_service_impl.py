# -*- coding: utf-8 -*-
"""
参数服务实现
一比一复刻参考项目 OptionServiceImpl.java

@author: FlowMaster
@since: 2025/10/05
"""

from typing import List, Dict
from sqlalchemy import select, update
from apps.system.core.service.option_service import OptionService
from apps.system.core.model.query.option_query import OptionQuery
from apps.system.core.model.req.option_req import OptionReq
from apps.system.core.model.req.option_value_reset_req import OptionValueResetReq
from apps.system.core.model.resp.option_resp import OptionResp
from apps.system.core.model.entity.option_entity import OptionEntity
from apps.system.core.enums.option_category_enum import OptionCategoryEnum
from apps.common.config.database.database_session import DatabaseSession
from apps.common.config.logging import get_logger
from apps.common.config.exception.global_exception_handler import BusinessException
from apps.common.context.user_context_holder import UserContextHolder

logger = get_logger(__name__)


class OptionServiceImpl(OptionService):
    """
    参数服务实现
    一比一复刻参考项目 OptionServiceImpl
    """

    async def list(self, query: OptionQuery) -> List[OptionResp]:
        """
        查询参数列表
        一比一复刻参考项目 OptionServiceImpl.list()
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                stmt = select(OptionEntity)

                # 按类别过滤
                if query.category:
                    stmt = stmt.where(OptionEntity.category == query.category)

                # 按键列表过滤
                if query.code and len(query.code) > 0:
                    stmt = stmt.where(OptionEntity.code.in_(query.code))

                # 按ID排序
                stmt = stmt.order_by(OptionEntity.id.asc())

                result = await session.execute(stmt)
                entities = result.scalars().all()

                # 转换为响应对象
                return [
                    OptionResp(
                        id=entity.id,
                        name=entity.name,
                        code=entity.code,
                        value=entity.value,
                        default_value=entity.default_value,
                        description=entity.description
                    )
                    for entity in entities
                ]

        except Exception as e:
            logger.error(f"查询参数列表失败: {e}", exc_info=True)
            raise BusinessException(f"查询参数列表失败: {str(e)}")

    async def get_by_category(self, category: OptionCategoryEnum) -> Dict[str, str]:
        """
        根据类别查询参数
        一比一复刻参考项目 OptionServiceImpl.getByCategory()

        返回 code -> value 的映射，如果value为空则使用defaultValue
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 查询指定类别的所有参数
                stmt = select(OptionEntity).where(
                    OptionEntity.category == category.value
                ).order_by(OptionEntity.id.asc())

                result = await session.execute(stmt)
                entities = result.scalars().all()

                # 转换为 code -> value 的字典
                # 一比一复刻参考项目: StrUtil.emptyIfNull(ObjectUtil.defaultIfNull(o.getValue(), o.getDefaultValue()))
                option_map = {}
                for entity in entities:
                    # 如果 value 不为空则使用 value，否则使用 default_value
                    value = entity.value if entity.value is not None else entity.default_value
                    # 如果还是 None，则使用空字符串
                    option_map[entity.code] = value if value is not None else ""

                return option_map

        except Exception as e:
            logger.error(f"根据类别查询参数失败 [{category.value}]: {e}", exc_info=True)
            raise BusinessException(f"根据类别查询参数失败: {str(e)}")

    async def update(self, options: List[OptionReq]) -> None:
        """
        批量修改参数
        一比一复刻参考项目 OptionServiceImpl.update()
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 获取当前用户ID
                current_user_id = UserContextHolder.get_user_id()
                if current_user_id is None:
                    current_user_id = 1  # 如果未登录，默认使用1（超级管理员）

                # 批量查询参数实体
                option_ids = [opt.id for opt in options]
                stmt = select(OptionEntity).where(OptionEntity.id.in_(option_ids))
                result = await session.execute(stmt)
                entities = result.scalars().all()

                # 构建code到entity的映射
                entity_map = {entity.code: entity for entity in entities}

                # 验证并更新
                for req in options:
                    entity = entity_map.get(req.code)
                    if entity is None:
                        raise BusinessException(f"参数 [{req.code}] 不存在")

                    # 如果有默认值，则值不能为空
                    if entity.default_value and not req.value:
                        raise BusinessException(f"参数 [{entity.name}] 的值不能为空")

                    # 更新值和修改人
                    entity.value = req.value
                    entity.update_user = current_user_id

                await session.flush()

                logger.info(f"批量修改参数成功，共 {len(options)} 个")

        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"批量修改参数失败: {e}", exc_info=True)
            raise BusinessException(f"批量修改参数失败: {str(e)}")

    async def reset_value(self, req: OptionValueResetReq) -> None:
        """
        重置参数值
        一比一复刻参考项目 OptionServiceImpl.resetValue()
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 校验：键列表和类别不能同时为空
                if not req.category and (not req.code or len(req.code) == 0):
                    raise BusinessException("键列表和类别不能同时为空")

                # 构建更新语句
                stmt = update(OptionEntity).values(value=None)

                # 按类别重置
                if req.category:
                    stmt = stmt.where(OptionEntity.category == req.category)
                # 按键列表重置
                elif req.code and len(req.code) > 0:
                    stmt = stmt.where(OptionEntity.code.in_(req.code))

                result = await session.execute(stmt)
                await session.flush()

                logger.info(f"重置参数值成功，影响行数: {result.rowcount}")

        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"重置参数值失败: {e}", exc_info=True)
            raise BusinessException(f"重置参数值失败: {str(e)}")
