# -*- coding: utf-8 -*-

"""
用户第三方账号关联实体 - 对应参考项目UserSocialDO
"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, BigInteger, Text, Index
from apps.common.base.model.entity.base_entity import Base


def utc_now():
    """返回当前UTC时间"""
    return datetime.now(timezone.utc)


class UserSocialEntity(Base):
    """
    用户第三方账号关联实体类

    一比一复刻参考项目UserSocialDO
    参考: refrence/continew-admin/.../UserSocialDO.java

    注意: 参考项目的UserSocialDO只有以下字段：
    - id, userId, source, openId, metaJson, lastLoginTime, createTime
    不继承审计字段基类（BaseCreateDO），只包含实际数据库字段
    """

    __tablename__ = "sys_user_social"
    __table_args__ = (
        # 一比一复刻参考项目：唯一索引 uk_source_open_id
        Index('uk_source_open_id', 'source', 'open_id', unique=True),
        {'comment': '用户社会化关联表'}
    )

    # ID - 数据库是bigint NOT NULL AUTO_INCREMENT
    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="ID"
    )

    # 用户ID - 数据库是bigint NOT NULL，必须用BigInteger
    user_id = Column(
        BigInteger,
        nullable=False,
        comment="用户ID"
    )

    # 来源 - varchar(255) NOT NULL
    source = Column(
        String(255),
        nullable=False,
        comment="来源"
    )

    # 开放ID - varchar(255) NOT NULL
    open_id = Column(
        String(255),
        nullable=False,
        comment="开放ID"
    )

    # 附加信息 - text DEFAULT NULL
    meta_json = Column(
        Text,
        nullable=True,
        comment="附加信息"
    )

    # 最后登录时间 - datetime DEFAULT NULL
    last_login_time = Column(
        DateTime,
        nullable=True,
        comment="最后登录时间"
    )

    # 创建时间 - datetime NOT NULL
    # 一比一复刻参考项目：只有createTime，没有create_user/update_user/update_time
    create_time = Column(
        DateTime,
        nullable=False,
        default=utc_now,
        comment="创建时间"
    )

    # 租户ID - bigint NOT NULL DEFAULT 0
    # 保持当前项目的多租户架构
    tenant_id = Column(
        BigInteger,
        nullable=False,
        default=0,
        comment="租户ID"
    )

    def __repr__(self):
        return f"<UserSocialEntity(id={self.id}, user_id={self.user_id}, source='{self.source}', open_id='{self.open_id}')>"