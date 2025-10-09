# -*- coding: utf-8 -*-

"""
用户实体 - 对应参考项目的UserDO
"""

from typing import Optional
from datetime import datetime
from pydantic import ConfigDict
from sqlalchemy import Column, String, BigInteger, Text, Boolean, DateTime
# 暂时移除relationship，避免循环引用问题
from apps.common.base.model.entity.base_entity import BaseEntity
from apps.common.enums.dis_enable_status_enum import DisEnableStatusEnum
from apps.common.enums.gender_enum import GenderEnum


class UserEntity(BaseEntity):
    """
    用户实体

    对应数据库表: sys_user
    对应Java实体: UserDO
    """

    __tablename__ = "sys_user"

    # 用户名（唯一）
    username: str = Column(String(64), nullable=False, unique=True, comment="用户名")

    # 昵称
    nickname: str = Column(String(64), nullable=False, comment="昵称")

    # 密码（加密存储）
    password: str = Column(String(255), nullable=False, comment="密码")

    # 性别
    gender: GenderEnum = Column(String(20), nullable=True, default=GenderEnum.UNKNOWN.value, comment="性别")

    # 邮箱（可加密存储）
    email: Optional[str] = Column(String(255), nullable=True, comment="邮箱")

    # 手机号码（可加密存储）
    phone: Optional[str] = Column(String(20), nullable=True, comment="手机号码")

    # 头像地址
    avatar: Optional[str] = Column(String(500), nullable=True, comment="头像地址")

    # 描述
    description: Optional[str] = Column(Text, nullable=True, comment="描述")

    # 状态（启用/禁用）
    status: DisEnableStatusEnum = Column(String(10), nullable=False, default=DisEnableStatusEnum.ENABLE.value, comment="状态")

    # 是否为系统内置数据
    is_system: bool = Column(Boolean, nullable=False, default=False, comment="是否为系统内置数据")

    # 最后一次修改密码时间
    pwd_reset_time: Optional[datetime] = Column(DateTime, nullable=True, comment="最后一次修改密码时间")

    # 部门ID
    dept_id: Optional[int] = Column(BigInteger, nullable=True, comment="部门ID")

    # ==========================================
    # 关联关系定义 - 暂时删除，等基本功能稳定后再添加
    # ==========================================

    # 用户角色关联
    # user_roles = relationship("UserRoleEntity", back_populates="user", cascade="all, delete-orphan")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "username": "admin",
                "nickname": "管理员",
                "password": "$2b$12$...",  # 加密后的密码
                "gender": "MALE",
                "email": "admin@example.com",
                "phone": "13800138000",
                "avatar": "/avatar/admin.jpg",
                "description": "系统管理员账号",
                "status": "ENABLE",
                "is_system": True,
                "pwd_reset_time": "2025-01-18T10:00:00Z",
                "dept_id": 1,
                "create_time": "2025-01-18T10:00:00Z",
                "update_time": "2025-01-18T10:00:00Z"
            }
        }
    )
    
    def __repr__(self) -> str:
        return f"<UserEntity(id={self.id}, username='{self.username}', nickname='{self.nickname}', status='{self.status}')>"
    
    def is_enabled(self) -> bool:
        """检查用户是否启用"""
        return self.status == DisEnableStatusEnum.ENABLE
    
    def is_system_user(self) -> bool:
        """检查是否为系统内置用户"""
        return self.is_system
    
    def is_password_expired(self, expire_days: int = 90) -> bool:
        """
        检查密码是否过期
        
        Args:
            expire_days: 密码过期天数，默认90天
            
        Returns:
            bool: 密码是否过期
        """
        if not self.pwd_reset_time:
            return False
        
        from datetime import timedelta
        expire_date = self.pwd_reset_time + timedelta(days=expire_days)
        return datetime.utcnow() > expire_date
    
    def get_display_name(self) -> str:
        """获取显示名称（优先昵称，其次用户名）"""
        return self.nickname or self.username
    
    def mask_sensitive_info(self) -> dict:
        """获取脱敏后的用户信息（隐藏密码等敏感信息）"""
        return {
            "id": self.id,
            "username": self.username,
            "nickname": self.nickname,
            "gender": self.gender,
            "email": self.email,
            "phone": self.phone,
            "avatar": self.avatar,
            "description": self.description,
            "status": self.status,
            "is_system": self.is_system,
            "dept_id": self.dept_id,
            "create_time": self.create_time,
            "update_time": self.update_time
        }