# -*- coding: utf-8 -*-

"""
系统配置服务 - 对应参考项目的OptionService
"""

from typing import List, Dict, Any
from sqlalchemy import select
from apps.system.core.model.entity.option_entity import OptionEntity
from apps.common.config.database.database_session import DatabaseSession
from apps.common.config.logging import get_logger

logger = get_logger(__name__)


class OptionService:
    """
    系统配置业务服务

    对应Java服务: OptionService
    提供系统配置查询等功能
    """

    async def list_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        根据分类查询系统配置列表
        一比一复刻参考项目的 list 方法

        Args:
            category: 配置分类（如 SITE）

        Returns:
            List[Dict[str, Any]]: 配置项列表，格式为 LabelValueResp
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 查询指定分类的配置项
                stmt = (
                    select(OptionEntity)
                    .where(OptionEntity.category == category)
                    .order_by(OptionEntity.id.asc())
                )
                result = await session.execute(stmt)
                options = result.scalars().all()

                # 转换为 LabelValueResp 格式
                # 参考项目逻辑: option.getValue() ?? option.getDefaultValue()
                return [
                    {
                        "label": option.code,
                        "value": option.value if option.value is not None else option.default_value
                    }
                    for option in options
                ]

        except Exception as e:
            logger.error(f"查询系统配置失败 [{category}]: {e}", exc_info=True)
            return []


# 全局服务实例
_option_service = None


def get_option_service() -> OptionService:
    """
    获取系统配置服务实例

    Returns:
        OptionService: 系统配置服务实例
    """
    global _option_service
    if _option_service is None:
        _option_service = OptionService()
    return _option_service