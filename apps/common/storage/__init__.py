"""
文件存储模块

提供统一的文件存储抽象层，支持多种存储后端（本地存储、对象存储等）。

主要组件:
    - StorageHandler: 存储处理器抽象接口
    - LocalStorageHandler: 本地文件系统存储实现
    - FileValidator: 文件验证器
    - StorageManager: 存储管理器（单例）
"""

from apps.common.storage.storage_handler import StorageHandler

__all__ = ["StorageHandler"]
