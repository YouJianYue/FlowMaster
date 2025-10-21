# -*- coding: utf-8 -*-

"""
数据库自动填充处理器

自动填充 create_user, create_time, update_user, update_time
"""

from datetime import datetime
from sqlalchemy import event
from apps.common.context.user_context_holder import UserContextHolder
from apps.common.config.logging import get_logger

logger = get_logger(__name__)


def auto_fill_create_fields(_mapper, _connection, target):
    """
    插入数据时自动填充创建信息
    """
    # 获取当前用户ID
    current_user_id = UserContextHolder.get_user_id()
    current_time = datetime.now()

    # 填充 create_user（如果为空）
    if hasattr(target, 'create_user') and target.create_user is None:
        target.create_user = current_user_id

    # 填充 create_time（如果为空）
    if hasattr(target, 'create_time') and target.create_time is None:
        target.create_time = current_time


def auto_fill_update_fields(_mapper, _connection, target):
    """
    更新数据时自动填充修改信息
    """
    # 获取当前用户ID
    current_user_id = UserContextHolder.get_user_id()
    current_time = datetime.now()

    # 填充 update_user（总是更新）
    if hasattr(target, 'update_user'):
        target.update_user = current_user_id

    # 填充 update_time（总是更新）
    if hasattr(target, 'update_time'):
        target.update_time = current_time


def register_auto_fill_listeners(base_class):
    """
    注册自动填充监听器

    Args:
        base_class: SQLAlchemy Base 类（所有实体的基类）

    - before_insert: 自动填充 create_user, create_time
    - before_update: 自动填充 update_user, update_time
    """
    # 监听 before_insert 事件（插入前）
    event.listen(base_class, 'before_insert', auto_fill_create_fields, propagate=True)

    # 监听 before_update 事件（更新前）
    event.listen(base_class, 'before_update', auto_fill_update_fields, propagate=True)

    logger.info("数据库自动填充监听器已注册")
