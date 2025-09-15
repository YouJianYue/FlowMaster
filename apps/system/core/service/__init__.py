# -*- coding: utf-8 -*-

from .message_service import MessageService
from .notice_service import NoticeService
from .dashboard_service import DashboardService

# 权限管理服务（新增）
from .permission_service import PermissionService

__all__ = [
    'MessageService',
    'NoticeService', 
    'DashboardService',
    'PermissionService'
]