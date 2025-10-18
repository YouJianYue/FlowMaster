# -*- coding: utf-8 -*-

"""
文件实体 - 对应参考项目的FileDO
"""

from typing import Optional
from sqlalchemy import Column, String, Integer, BigInteger, Text, ForeignKey
from apps.common.base.model.entity.tenant_base_entity import TenantBaseEntity


class FileEntity(TenantBaseEntity):
    """
    文件实体

    对应数据库表: sys_file
    对应参考项目: FileDO
    """

    __tablename__ = "sys_file"

    # 文件名称
    name: str = Column(String(255), nullable=False, comment="文件名称")

    # 原始名称
    original_name: str = Column(String(255), nullable=False, comment="原始名称")

    # 大小（字节）
    size: Optional[int] = Column(BigInteger, nullable=True, comment="大小（字节）")

    # 上级目录
    parent_path: str = Column(String(512), nullable=False, default='/', comment="上级目录")

    # 路径
    path: str = Column(String(512), nullable=False, comment="路径")

    # 扩展名
    extension: Optional[str] = Column(String(32), nullable=True, comment="扩展名")

    # 内容类型
    content_type: Optional[str] = Column(String(255), nullable=True, comment="内容类型")

    # 类型（0: 目录；1：其他；2：图片；3：文档；4：视频；5：音频）
    type: int = Column(Integer, nullable=False, default=1, comment="类型")

    # SHA256值
    sha256: Optional[str] = Column(String(256), nullable=True, comment="SHA256值")

    # 元数据（使用file_metadata避免与SQLAlchemy的metadata冲突）
    file_metadata: Optional[str] = Column("metadata", Text, nullable=True, comment="元数据")

    # 缩略图名称
    thumbnail_name: Optional[str] = Column(String(255), nullable=True, comment="缩略图名称")

    # 缩略图大小（字节）
    thumbnail_size: Optional[int] = Column(BigInteger, nullable=True, comment="缩略图大小（字节）")

    # 缩略图元数据
    thumbnail_metadata: Optional[str] = Column(Text, nullable=True, comment="缩略图元数据")

    # 存储ID
    storage_id: int = Column(Integer, ForeignKey('sys_storage.id'), nullable=False, comment="存储ID")

    def __repr__(self) -> str:
        return f"<FileEntity(id={self.id}, name='{self.name}', type={self.type})>"