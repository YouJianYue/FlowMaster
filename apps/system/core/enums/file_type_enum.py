# -*- coding: utf-8 -*-
"""
文件类型枚举

一比一复刻参考项目 FileTypeEnum.java
@author: FlowMaster
@since: 2025/10/12
"""

from enum import Enum
from typing import List


class FileTypeEnum(int, Enum):
    """
    文件类型枚举

    一比一复刻参考项目 FileTypeEnum.java
    """

    # 目录
    DIR = 0

    # 其他
    UNKNOWN = 1

    # 图片
    IMAGE = 2

    # 文档
    DOC = 3

    # 视频
    VIDEO = 4

    # 音频
    AUDIO = 5

    @property
    def description(self) -> str:
        """获取描述"""
        mapping = {
            self.DIR: "目录",
            self.UNKNOWN: "其他",
            self.IMAGE: "图片",
            self.DOC: "文档",
            self.VIDEO: "视频",
            self.AUDIO: "音频",
        }
        return mapping[self]

    @property
    def extensions(self) -> List[str]:
        """获取支持的扩展名列表"""
        mapping = {
            self.DIR: [],
            self.UNKNOWN: [],
            self.IMAGE: ["jpg", "jpeg", "png", "gif", "bmp", "webp", "ico", "psd", "tiff", "dwg", "jxr", "apng", "xcf"],
            self.DOC: ["txt", "pdf", "doc", "xls", "ppt", "docx", "xlsx", "pptx"],
            self.VIDEO: ["mp4", "avi", "mkv", "flv", "webm", "wmv", "m4v", "mov", "mpg", "rmvb", "3gp"],
            self.AUDIO: ["mp3", "flac", "wav", "ogg", "midi", "m4a", "aac", "amr", "ac3", "aiff"],
        }
        return mapping[self]

    @classmethod
    def get_by_extension(cls, extension: str) -> 'FileTypeEnum':
        """
        根据扩展名查询文件类型

        Args:
            extension: 文件扩展名

        Returns:
            FileTypeEnum: 文件类型
        """
        if not extension:
            return cls.UNKNOWN

        ext_lower = extension.lower()
        for file_type in cls:
            if ext_lower in file_type.extensions:
                return file_type

        return cls.UNKNOWN

    @classmethod
    def get_all_extensions(cls) -> List[str]:
        """获取所有支持的扩展名"""
        all_exts = []
        for file_type in cls:
            all_exts.extend(file_type.extensions)
        return all_exts
