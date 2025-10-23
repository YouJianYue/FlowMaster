"""
存储处理器抽象接口

定义文件存储系统的核心接口，支持多种存储实现（本地存储、对象存储等）。
所有存储处理器必须实现此接口以确保一致的行为。
"""

from abc import ABC, abstractmethod
from typing import Optional
from fastapi import UploadFile


class StorageHandler(ABC):
    """存储处理器抽象接口

    定义文件存储的核心操作接口，包括上传、下载、删除、目录创建等。
    采用策略模式设计，允许运行时切换不同的存储实现。

    实现类:
        - LocalStorageHandler: 本地文件系统存储
        - S3StorageHandler: AWS S3对象存储（待实现）
        - OSSStorageHandler: 阿里云OSS对象存储（待实现）
    """

    @abstractmethod
    async def upload_file(self, file: UploadFile, path: str) -> str:
        """上传文件到存储系统

        Args:
            file: FastAPI上传文件对象，包含文件内容和元数据
            path: 存储路径（相对路径），如 "2024/01/15/document_123456.pdf"

        Returns:
            str: 文件存储后的相对路径

        Raises:
            ValueError: 路径不安全（包含..等非法字符）
            RuntimeError: 上传失败（磁盘空间不足、权限问题等）

        Example:
            >>> handler = LocalStorageHandler(root_path="./data/files")
            >>> stored_path = await handler.upload_file(file, "2024/01/15/test.pdf")
            >>> print(stored_path)  # "2024/01/15/test.pdf"
        """
        pass

    @abstractmethod
    async def download_file(self, path: str) -> bytes:
        """从存储系统下载文件

        Args:
            path: 文件存储路径（相对路径）

        Returns:
            bytes: 文件内容字节数据

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 路径不安全
            RuntimeError: 下载失败

        Example:
            >>> content = await handler.download_file("2024/01/15/test.pdf")
            >>> len(content)  # 文件大小（字节）
        """
        pass

    @abstractmethod
    async def delete_file(self, path: str) -> bool:
        """删除存储系统中的文件

        Args:
            path: 文件存储路径（相对路径）

        Returns:
            bool: 删除成功返回True，文件不存在返回False

        Raises:
            ValueError: 路径不安全
            RuntimeError: 删除失败（权限问题等）

        Example:
            >>> success = await handler.delete_file("2024/01/15/test.pdf")
            >>> print(success)  # True 或 False
        """
        pass

    @abstractmethod
    async def create_directory(self, path: str) -> bool:
        """创建目录

        Args:
            path: 目录路径（相对路径）

        Returns:
            bool: 创建成功返回True

        Raises:
            ValueError: 路径不安全
            RuntimeError: 创建失败

        Example:
            >>> success = await handler.create_directory("2024/01/15")
            >>> print(success)  # True
        """
        pass

    @abstractmethod
    def build_url(self, path: str) -> str:
        """构建文件访问URL

        Args:
            path: 文件存储路径（相对路径）

        Returns:
            str: 完整的访问URL

        Example:
            >>> url = handler.build_url("2024/01/15/test.pdf")
            >>> print(url)  # "/files/2024/01/15/test.pdf" 或 "https://cdn.example.com/2024/01/15/test.pdf"
        """
        pass

    @abstractmethod
    def get_type(self) -> str:
        """获取存储类型标识符

        Returns:
            str: 存储类型（LOCAL、S3、OSS等）

        Example:
            >>> storage_type = handler.get_type()
            >>> print(storage_type)  # "LOCAL"
        """
        pass
