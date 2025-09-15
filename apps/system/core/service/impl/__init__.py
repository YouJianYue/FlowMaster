# -*- coding: utf-8 -*-

from .message_service_impl import MessageServiceImpl
from .notice_service_impl import NoticeServiceImpl
from .dashboard_service_impl import DashboardServiceImpl

# 权限管理服务实现（新增）
from .permission_service_impl import PermissionServiceImpl

__all__ = [
    'MessageServiceImpl',
    'NoticeServiceImpl',
    'DashboardServiceImpl',
    'PermissionServiceImpl'
]