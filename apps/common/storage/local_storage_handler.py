"""
本地文件系统存储处理器

实现基于本地文件系统的存储功能，包括文件上传、下载、删除、目录管理等。
支持异步操作，确保高性能和安全性。
"""

import os
import aiofiles
from pathlib import Path
from fastapi import UploadFile

from apps.common.storage.storage_handler import StorageHandler
from apps.common.config.logging import get_logger

logger = get_logger(__name__)


class LocalStorageHandler(StorageHandler):
    """本地文件系统存储处理器

    使用本地文件系统存储文件，提供完整的文件管理功能。
    支持异步IO操作，确保高性能。包含完善的安全检查，防止路径遍历攻击。

    Attributes:
        root_path: 存储根目录的绝对路径
        domain: 自定义访问域名（可选）
        max_file_size: 最大文件大小限制（字节）
    """

    def __init__(
        self,
        root_path: str,
        domain: str = "",
        max_file_size: int = 100 * 1024 * 1024
    ):
        """初始化本地存储处理器

        Args:
            root_path: 存储根目录路径（支持相对路径和绝对路径）
            domain: 自定义访问域名，用于构建URL（可选）
            max_file_size: 最大文件大小限制（字节），默认100MB

        Raises:
            PermissionError: 存储目录无写入权限
        """
        self.root_path = Path(root_path).resolve()
        self.domain = domain
        self.max_file_size = max_file_size

        # 确保根目录存在
        self.root_path.mkdir(parents=True, exist_ok=True)

        # 验证根目录权限
        if not os.access(self.root_path, os.W_OK):
            raise PermissionError(f"存储目录无写入权限: {self.root_path}")

        logger.info(f"本地存储处理器初始化完成: root_path={self.root_path}, domain={self.domain}")

    async def upload_file(self, file: UploadFile, path: str) -> str:
        """上传文件到本地存储

        Args:
            file: FastAPI上传文件对象
            path: 存储路径（相对路径）

        Returns:
            str: 文件存储后的相对路径

        Raises:
            ValueError: 路径不安全或文件大小超过限制
            RuntimeError: 文件上传失败
        """
        try:
            # 安全路径处理
            safe_path = self._normalize_path(path)

            # 构建完整路径
            full_path = self.root_path / safe_path

            # 验证路径安全
            self._validate_path(full_path)

            # 确保父目录存在
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # 检查文件大小
            content = await file.read()
            if len(content) > self.max_file_size:
                raise ValueError(
                    f"文件大小超过限制: {len(content)} > {self.max_file_size} "
                    f"({self.max_file_size / 1024 / 1024:.1f}MB)"
                )

            # 保存文件
            async with aiofiles.open(full_path, 'wb') as f:
                await f.write(content)

            logger.info(f"文件上传成功: {full_path} ({len(content)} bytes)")

            # 返回相对路径（使用正斜杠，兼容Windows和Linux）
            return safe_path.as_posix()

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"文件上传失败: path={path}, error={e}", exc_info=True)
            raise RuntimeError(f"文件上传失败: {str(e)}")

    async def download_file(self, path: str) -> bytes:
        """从本地存储下载文件

        Args:
            path: 文件存储路径（相对路径）

        Returns:
            bytes: 文件内容字节数据

        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 路径不安全或路径不是文件
            RuntimeError: 文件下载失败
        """
        try:
            # 安全路径处理
            safe_path = self._normalize_path(path)

            # 构建完整路径
            full_path = self.root_path / safe_path

            # 验证路径安全
            self._validate_path(full_path)

            # 检查文件是否存在
            if not full_path.exists():
                raise FileNotFoundError(f"文件不存在: {safe_path}")

            # 检查是否为文件
            if not full_path.is_file():
                raise ValueError(f"路径不是文件: {safe_path}")

            # 读取文件内容
            async with aiofiles.open(full_path, 'rb') as f:
                content = await f.read()

            logger.debug(f"文件下载成功: {safe_path} ({len(content)} bytes)")
            return content

        except (FileNotFoundError, ValueError):
            raise
        except Exception as e:
            logger.error(f"文件下载失败: path={path}, error={e}", exc_info=True)
            raise RuntimeError(f"文件下载失败: {str(e)}")

    async def delete_file(self, path: str) -> bool:
        """删除本地存储文件

        Args:
            path: 文件存储路径（相对路径）

        Returns:
            bool: 删除成功返回True，文件不存在返回False

        Raises:
            ValueError: 路径不安全
            RuntimeError: 文件删除失败
        """
        try:
            # 安全路径处理
            safe_path = self._normalize_path(path)

            # 构建完整路径
            full_path = self.root_path / safe_path

            # 验证路径安全
            self._validate_path(full_path)

            # 检查文件是否存在
            if not full_path.exists():
                logger.warning(f"文件不存在，跳过删除: {safe_path}")
                return False

            # 检查是否为文件
            if not full_path.is_file():
                logger.warning(f"路径不是文件，跳过删除: {safe_path}")
                return False

            # 删除文件
            full_path.unlink()
            logger.info(f"文件删除成功: {safe_path}")
            return True

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"文件删除失败: path={path}, error={e}", exc_info=True)
            raise RuntimeError(f"文件删除失败: {str(e)}")

    async def create_directory(self, path: str) -> bool:
        """创建目录

        Args:
            path: 目录路径（相对路径）

        Returns:
            bool: 创建成功返回True

        Raises:
            ValueError: 路径不安全
            RuntimeError: 目录创建失败
        """
        try:
            # 安全路径处理
            safe_path = self._normalize_path(path)

            # 构建完整路径
            full_path = self.root_path / safe_path

            # 验证路径安全
            self._validate_path(full_path)

            # 创建目录
            full_path.mkdir(parents=True, exist_ok=True)

            logger.info(f"目录创建成功: {safe_path}")
            return True

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"目录创建失败: path={path}, error={e}", exc_info=True)
            raise RuntimeError(f"目录创建失败: {str(e)}")

    def build_url(self, path: str) -> str:
        """构建文件访问URL

        Args:
            path: 文件存储路径（相对路径）

        Returns:
            str: 完整的访问URL
        """
        try:
            # 确保路径使用正斜杠���兼容Windows）
            normalized_path = path.replace('\\', '/').lstrip('/')

            if self.domain:
                # 使用自定义域名
                return f"{self.domain.rstrip('/')}/{normalized_path}"
            else:
                # 使用相对路径，由nginx或其他服务提供静态文件访问
                return f"/files/{normalized_path}"

        except Exception as e:
            logger.error(f"构建URL失败: path={path}, error={e}")
            # 降级处理
            return f"/files/{path.replace('\\', '/').lstrip('/')}"

    def get_type(self) -> str:
        """获取存储类型

        Returns:
            str: 存储类型标识符 "LOCAL"
        """
        return "LOCAL"

    def _normalize_path(self, path: str) -> Path:
        """标准化路径，防止路径遍历攻击

        Args:
            path: 原始路径

        Returns:
            Path: 标准化的相对路径

        Raises:
            ValueError: 路径包含非法字符
        """
        # 移除前导和尾随的斜杠
        path = path.strip('/')

        # 使用pathlib处理路径
        path_obj = Path(path)

        # 确保路径是相对的，不包含..
        if '..' in str(path_obj.as_posix()):
            raise ValueError("路径包含非法字符: ..")

        # 返回标准化的路径
        return path_obj

    def _validate_path(self, full_path: Path) -> None:
        """验证路径安全性

        Args:
            full_path: 完整的文件系统路径

        Raises:
            ValueError: 路径不安全
        """
        # 确保路径在根目录下
        try:
            full_path.resolve().relative_to(self.root_path)
        except ValueError:
            raise ValueError(f"路径超出存储根目录: {full_path}")

        # 检查路径长度
        if len(str(full_path)) > 4096:
            raise ValueError("路径过长")
