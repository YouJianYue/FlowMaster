"""
文件存储配置属性类

此模块提供文件存储系统的配置管理，包括本地存储路径、文件大小限制、允许的文件类型等。
配置通过环境变量读取，支持灵活的部署配置。
"""

import os
from typing import Set


class StorageProperties:
    """文件存储配置属性类

    通过环境变量配置文件存储相关参数，包括：
    - 本地存储根路径和域名
    - 文件大小和类型限制
    - 文件名长度限制

    注意：此类不能被实例化，所有属性均为类属性
    """

    # ==================== 本地存储配置 ====================

    LOCAL_ROOT_PATH: str = os.getenv(
        "STORAGE_LOCAL_ROOT_PATH",
        "./data/files"
    )
    """本地存储根目录路径

    环境变量: STORAGE_LOCAL_ROOT_PATH
    默认值: ./data/files
    """

    LOCAL_DOMAIN: str = os.getenv("STORAGE_LOCAL_DOMAIN", "")
    """自定义访问域名（可选）

    环境变量: STORAGE_LOCAL_DOMAIN
    默认值: 空字符串（使用相对路径）
    示例: https://cdn.example.com
    """

    # ==================== 文件限制配置 ====================

    MAX_FILE_SIZE: int = int(os.getenv(
        "STORAGE_MAX_FILE_SIZE",
        str(100 * 1024 * 1024)  # 100MB
    ))
    """最大文件大小限制（字节）

    环境变量: STORAGE_MAX_FILE_SIZE
    默认值: 104857600 (100MB)
    """

    MAX_FILENAME_LENGTH: int = int(os.getenv(
        "STORAGE_MAX_FILENAME_LENGTH",
        "255"
    ))
    """文件名最大长度限制

    环境变量: STORAGE_MAX_FILENAME_LENGTH
    默认值: 255
    """

    # ==================== 文件类型配置 ====================

    ALLOWED_EXTENSIONS: Set[str] = set(
        os.getenv(
            "STORAGE_ALLOWED_EXTENSIONS",
            "pdf,doc,docx,xls,xlsx,ppt,pptx,txt,md,rtf,"
            "jpg,jpeg,png,gif,bmp,svg,webp,ico,"
            "mp3,wav,wma,aac,flac,ogg,m4a,"
            "mp4,avi,mov,wmv,flv,mkv,webm,mpg,mpeg,"
            "zip,rar,7z,tar,gz,bz2,xz"
        ).split(",")
    )
    """允许上传的文件扩展名集合

    环境变量: STORAGE_ALLOWED_EXTENSIONS
    默认值: 常见文档、图片、音视频、压缩包格式
    格式: 逗号分隔的扩展名列表（不含点号）
    """

    def __init__(self):
        """禁止实例化"""
        raise RuntimeError("StorageProperties cannot be instantiated")
