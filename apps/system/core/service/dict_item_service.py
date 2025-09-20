# -*- coding: utf-8 -*-

"""
字典项服务 - 对应参考项目的DictItemService
"""

from typing import List, Dict, Any
from sqlalchemy import select
from apps.system.core.model.entity.dict_item_entity import DictItemEntity
from apps.system.core.model.entity.dict_entity import DictEntity
from apps.common.config.database.database_session import DatabaseSession
from apps.common.config.logging import get_logger

logger = get_logger(__name__)


class DictItemService:
    """
    字典项业务服务

    对应Java服务: DictItemService
    提供字典项查询等功能
    """

    async def list_by_dict_code(self, dict_code: str) -> List[Dict[str, Any]]:
        """
        根据字典编码查询字典项列表
        一比一复刻参考项目的 listByDictCode 方法

        Args:
            dict_code: 字典编码

        Returns:
            List[Dict[str, Any]]: 字典项列表，格式为 LabelValueResp
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 先根据字典编码查询字典ID
                dict_stmt = select(DictEntity.id).where(DictEntity.code == dict_code)
                dict_result = await session.execute(dict_stmt)
                dict_id = dict_result.scalar_one_or_none()

                if dict_id is None:
                    logger.warning(f"字典编码不存在: {dict_code}")
                    return []

                # 查询字典项（只查询启用状态的）
                stmt = (
                    select(DictItemEntity)
                    .where(DictItemEntity.dict_id == dict_id)
                    .where(DictItemEntity.status == 1)  # 启用状态
                    .order_by(DictItemEntity.sort.asc())
                )
                result = await session.execute(stmt)
                dict_items = result.scalars().all()

                # 转换为 LabelValueResp 格式
                return [
                    {
                        "label": item.label,
                        "value": item.value
                    }
                    for item in dict_items
                ]

        except Exception as e:
            logger.error(f"查询字典项失败 [{dict_code}]: {e}", exc_info=True)
            return []


# 全局服务实例
_dict_item_service = None


def get_dict_item_service() -> DictItemService:
    """
    获取字典项服务实例

    Returns:
        DictItemService: 字典项服务实例
    """
    global _dict_item_service
    if _dict_item_service is None:
        _dict_item_service = DictItemService()
    return _dict_item_service