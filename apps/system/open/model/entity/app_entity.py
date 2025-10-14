# -*- coding: utf-8 -*-

"""
应用实体 - 一比一复刻AppDO
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, BigInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from apps.common.base.model.entity.base_entity import BaseEntity


class AppEntity(BaseEntity):
    """
    应用实体

    一比一复刻参考项目 AppDO.java

    @TableName("sys_app")
    public class AppDO extends BaseDO

    BaseDO 包含字段：ID、创建人、创建时间、修改人、修改时间
    """

    __tablename__ = "sys_app"
    __table_args__ = {"comment": "应用管理表"}

    # 应用名称
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="应用名称"
    )

    # Access Key（访问密钥）- 加密存储
    access_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        comment="Access Key（访问密钥）"
    )

    # Secret Key（私有密钥）- 加密存储
    secret_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Secret Key（私有密钥）"
    )

    # 失效时间
    expire_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="失效时间"
    )

    # 描述
    description: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="描述"
    )

    # 状态（1启用 2禁用）
    status: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=1,
        comment="状态（1启用 2禁用）"
    )

    def is_expired(self) -> bool:
        """
        是否已过期

        一比一复刻参考项目:
        public boolean isExpired() {
            if (expireTime == null) {
                return false;
            }
            return LocalDateTime.now().isAfter(expireTime);
        }

        Returns:
            bool: True-已过期，False-未过期
        """
        if self.expire_time is None:
            return False
        return datetime.now() > self.expire_time

    def is_enabled(self) -> bool:
        """
        是否启用

        Returns:
            bool: True-启用，False-禁用
        """
        return self.status == 1
