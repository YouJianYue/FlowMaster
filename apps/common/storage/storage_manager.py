"""
存储管理器

单例模式管理多个存储处理器，支持运行时动态切换存储后端。
提供存储处理器的注册、获取、切换等功能。
"""

from typing import Optional, Dict

from apps.common.storage.storage_handler import StorageHandler
from apps.common.storage.local_storage_handler import LocalStorageHandler
from apps.common.config.logging import get_logger

logger = get_logger(__name__)


class StorageManager:
    """存储管理器（单例模式）

    管理系统中的所有存储处理器，支持多种存储后端共存。
    使用代码级单例模式，确保全局只有一个存储管理器实例。

    Attributes:
        _handlers: 存储处理器字典 {code: handler}
        _default_storage: 默认存储配置编码

    Example:
        >>> from apps.common.storage.storage_manager import storage_manager
        >>>
        >>> # 注册本地存储
        >>> local_handler = LocalStorageHandler(root_path="./data/files")
        >>> storage_manager.register_storage("local_storage", local_handler, is_default=True)
        >>>
        >>> # 获取默认存储处理器
        >>> handler = storage_manager.get_default_handler()
        >>> stored_path = await handler.upload_file(file, "2024/01/15/test.pdf")
    """

    def __init__(self):
        """初始化存储管理器"""
        self._handlers: Dict[str, StorageHandler] = {}
        self._default_storage: Optional[str] = None
        logger.debug("存储管理器初始化完成")

    def register_storage(
        self,
        code: str,
        handler: StorageHandler,
        is_default: bool = False
    ) -> None:
        """注册存储处理器

        Args:
            code: 存储配置编码（唯一标识符）
            handler: 存储处理器实例
            is_default: 是否设为默认存储

        Raises:
            ValueError: 存储编码或处理器为空

        Example:
            >>> local_handler = LocalStorageHandler(root_path="./data/files")
            >>> storage_manager.register_storage(
            ...     code="local_storage",
            ...     handler=local_handler,
            ...     is_default=True
            ... )
        """
        if not code or not handler:
            raise ValueError("存储编码和处理器不能为空")

        self._handlers[code] = handler

        if is_default or self._default_storage is None:
            self._default_storage = code
            logger.info(f"设置默认存储: {code}")

        logger.info(f"注册存储处理器: code={code}, type={handler.get_type()}")

    def get_handler(self, code: Optional[str] = None) -> StorageHandler:
        """获取存储处理器

        Args:
            code: 存储配置编码，为None时使用默认存储

        Returns:
            StorageHandler: 存储处理器实例

        Raises:
            ValueError: 存储配置不存在

        Example:
            >>> # 获取默认存储
            >>> handler = storage_manager.get_handler()
            >>>
            >>> # 获取指定存储
            >>> handler = storage_manager.get_handler("local_storage")
        """
        if code is None:
            code = self._default_storage

        if code not in self._handlers:
            available_codes = list(self._handlers.keys())
            raise ValueError(
                f"存储配置不存在: {code}, 可用配置: {available_codes}"
            )

        return self._handlers[code]

    def get_default_handler(self) -> StorageHandler:
        """获取默认存储处理器

        Returns:
            StorageHandler: 默认存储处理器实例

        Raises:
            ValueError: 没有配置默认存储

        Example:
            >>> handler = storage_manager.get_default_handler()
            >>> stored_path = await handler.upload_file(file, "test.pdf")
        """
        if self._default_storage is None:
            raise ValueError("没有配置默认存储")

        return self._handlers[self._default_storage]

    def list_handlers(self) -> Dict[str, str]:
        """获取所有存储处理器信息

        Returns:
            Dict[str, str]: 存储编码到存储类型的映射

        Example:
            >>> handlers = storage_manager.list_handlers()
            >>> print(handlers)
            {'local_storage': 'LOCAL', 'oss_storage': 'OSS'}
        """
        return {
            code: handler.get_type()
            for code, handler in self._handlers.items()
        }

    def set_default_storage(self, code: str) -> None:
        """设置默认存储

        Args:
            code: 存储配置编码

        Raises:
            ValueError: 存储配置不存在

        Example:
            >>> storage_manager.set_default_storage("local_storage")
        """
        if code not in self._handlers:
            raise ValueError(f"存储配置不存在: {code}")

        self._default_storage = code
        logger.info(f"设置默认存储: {code}")

    def remove_storage(self, code: str) -> None:
        """移除存储处理器

        如果移除的是默认存储，会自动选择第一个可用存储作为默认存储。

        Args:
            code: 存储配置编码

        Example:
            >>> storage_manager.remove_storage("old_storage")
        """
        if code not in self._handlers:
            return

        del self._handlers[code]
        logger.info(f"移除存储处理器: {code}")

        # 如果移除的是默认存储，重新选择默认存储
        if self._default_storage == code:
            if self._handlers:
                self._default_storage = next(iter(self._handlers.keys()))
                logger.info(f"自动设置新的默认存储: {self._default_storage}")
            else:
                self._default_storage = None
                logger.warning("没有可用的存储配置")

    def has_storage(self, code: str) -> bool:
        """检查存储配置是否存在

        Args:
            code: 存储配置编码

        Returns:
            bool: 存在返回True，否则返回False

        Example:
            >>> if storage_manager.has_storage("local_storage"):
            ...     handler = storage_manager.get_handler("local_storage")
        """
        return code in self._handlers

    def get_default_code(self) -> Optional[str]:
        """获取默认存储配置编码

        Returns:
            Optional[str]: 默认存储配置编码，未配置时返回None

        Example:
            >>> code = storage_manager.get_default_code()
            >>> print(code)  # "local_storage"
        """
        return self._default_storage


# 全局单例实例
storage_manager = StorageManager()
