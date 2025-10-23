"""
文件验证器

提供文件上传的安全验证功能，包括文件类型、大小、文件名等验证。
支持白名单机制，确保只允许上传安全的文件类型。
"""

import os
import re
import uuid
import mimetypes
from typing import Set
from datetime import datetime

from apps.common.config.storage_properties import StorageProperties
from apps.common.config.logging import get_logger

logger = get_logger(__name__)


class FileValidator:
    """文件验证器

    提供文件上传前的安全验证，包括：
    - 文件扩展名白名单验证
    - 文件大小限制验证
    - 内容类型一致性验证
    - 文件名安全处理（移除危险字符）
    - 唯一文件名生成

    注意：此类不能被实例化，所有方法均为类方法
    """

    # 允许的文件扩展名（从配置读取）
    ALLOWED_EXTENSIONS: Set[str] = StorageProperties.ALLOWED_EXTENSIONS

    # 文件大小限制（从配置读取）
    MAX_FILE_SIZE: int = StorageProperties.MAX_FILE_SIZE

    # 文件名长度限制（从配置读取）
    MAX_FILENAME_LENGTH: int = StorageProperties.MAX_FILENAME_LENGTH

    @classmethod
    def validate_file_extension(cls, filename: str) -> bool:
        """验证文件扩展名是否在白名单中

        Args:
            filename: 文件名

        Returns:
            bool: 扩展名允许返回True，否则返回False

        Example:
            >>> FileValidator.validate_file_extension("document.pdf")
            True
            >>> FileValidator.validate_file_extension("virus.exe")
            False
        """
        if not filename or '.' not in filename:
            logger.warning(f"文件名无效: {filename}")
            return False

        try:
            ext = filename.rsplit('.', 1)[1].lower()
            is_allowed = ext in cls.ALLOWED_EXTENSIONS

            if not is_allowed:
                logger.warning(f"文件扩展名不允许: {ext}")

            return is_allowed

        except Exception as e:
            logger.error(f"验证文件扩展名失败: {e}")
            return False

    @classmethod
    def validate_file_size(cls, file_size: int) -> bool:
        """验证文件大小是否在限制内

        Args:
            file_size: 文件大小（字节）

        Returns:
            bool: 文件大小允许返回True，否则返回False

        Example:
            >>> FileValidator.validate_file_size(1024 * 1024)  # 1MB
            True
            >>> FileValidator.validate_file_size(200 * 1024 * 1024)  # 200MB
            False
        """
        if file_size <= 0:
            logger.warning(f"文件大小无效: {file_size}")
            return False

        is_allowed = file_size <= cls.MAX_FILE_SIZE

        if not is_allowed:
            logger.warning(
                f"文件大小超过限制: {file_size} > {cls.MAX_FILE_SIZE} "
                f"({cls.MAX_FILE_SIZE / 1024 / 1024:.1f}MB)"
            )

        return is_allowed

    @classmethod
    def validate_content_type(cls, content_type: str, filename: str) -> bool:
        """验证内容类型与文件扩展名的一致性

        Args:
            content_type: HTTP Content-Type
            filename: 文件名

        Returns:
            bool: 验证通过返回True，否则返回False

        Example:
            >>> FileValidator.validate_content_type("application/pdf", "doc.pdf")
            True
            >>> FileValidator.validate_content_type("image/png", "doc.pdf")
            False
        """
        if not content_type or not filename:
            return True  # 跳过验证

        try:
            # 获取文件扩展名对应的内容类型
            ext = filename.rsplit('.', 1)[1].lower()
            expected_type, _ = mimetypes.guess_type(f"test.{ext}")

            if expected_type and content_type != expected_type:
                logger.warning(
                    f"内容类型不匹配: {content_type} != {expected_type} "
                    f"(filename={filename})"
                )
                return False

            return True

        except Exception as e:
            logger.error(f"验证内容类型失败: {e}")
            return True  # 验证失败时不阻止上传

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """清理文件名，移除危险字符

        移除路径分隔符、特殊字符、控制字符等，确保文件名安全。

        Args:
            filename: 原始文件名

        Returns:
            str: 清理后的文件名

        Example:
            >>> FileValidator.sanitize_filename("../../etc/passwd")
            "etc_passwd"
            >>> FileValidator.sanitize_filename("file<>:name.txt")
            "filename.txt"
        """
        if not filename:
            return "unknown"

        # 移除路径分隔符，防止路径注入
        filename = os.path.basename(filename)

        # 移除特殊字符和控制字符
        filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', filename)

        # 移除连续的点号
        filename = re.sub(r'\.{2,}', '.', filename)

        # 移除前导和尾随的点号和空格
        filename = filename.strip('. ')

        # 如果文件名为空，使用默认值
        if not filename:
            filename = "unknown"

        # 限制长度
        if len(filename) > cls.MAX_FILENAME_LENGTH:
            name, ext = os.path.splitext(filename)
            max_name_length = cls.MAX_FILENAME_LENGTH - len(ext)
            filename = name[:max_name_length] + ext

        return filename

    @classmethod
    def generate_unique_filename(
        cls,
        original_name: str,
        timestamp: str = None
    ) -> str:
        """生成唯一文件名

        使用时间戳和UUID生成唯一文件名，避免文件名冲突。
        格式: {timestamp}_{uuid8}.{ext}

        Args:
            original_name: 原始文件名
            timestamp: 时间戳（可选），默认使用当前时间

        Returns:
            str: 唯一文件名

        Example:
            >>> FileValidator.generate_unique_filename("document.pdf")
            "20240115143025_a3f2b8c9.pdf"
        """
        if not timestamp:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

        # 清理原始文件名
        clean_name = cls.sanitize_filename(original_name)

        # 分离文件名和扩展名
        name, ext = os.path.splitext(clean_name)

        # 生成唯一标识符
        unique_id = uuid.uuid4().hex[:8]

        # 组合唯一文件名
        unique_filename = f"{timestamp}_{unique_id}{ext}"

        return unique_filename

    def __init__(self):
        """禁止实例化"""
        raise RuntimeError("FileValidator cannot be instantiated")
