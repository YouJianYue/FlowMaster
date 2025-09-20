# -*- coding: utf-8 -*-

"""
用户信息响应模型 - 完全匹配参考项目的字段结构
使用Pydantic自动处理snake_case到camelCase转换
"""

from typing import List, Optional, Set
from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel


class UserInfoResp(BaseModel):
    """
    用户信息响应模型
    
    完全匹配参考项目的用户信息返回格式
    Python字段使用snake_case，API响应自动转换为camelCase
    """
    
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "username": "admin",
                "nickname": "超级管理员",
                "gender": 1,
                "email": "admin@continew.top",
                "phone": "13800138000",
                "avatar": "",
                "description": "系统管理员",
                "pwdResetTime": "2023-08-08T08:08:08",
                "pwdExpired": False,
                "registrationDate": "2023-08-08",
                "deptId": 1,
                "deptName": "总办",
                "permissions": [
                    "system:menu:list",
                    "system:menu:create",
                    "system:menu:update",
                    "system:menu:delete",
                    "system:user:list",
                    "system:user:create",
                    "system:user:update",
                    "system:user:delete"
                ],
                "roles": ["super_admin"],
                "roleNames": ["超级管理员"]
            }
        }
    )
    
    # 用户ID
    id: int = Field(..., description="用户ID")
    
    # 用户名
    username: str = Field(..., description="用户名")
    
    # 昵称
    nickname: Optional[str] = Field(None, description="用户昵称")
    
    # 性别：1=男，2=女，3=未知
    gender: int = Field(1, description="性别（1：男；2：女；3：未知）")
    
    # 邮箱
    email: Optional[str] = Field("", description="邮箱")
    
    # 手机号
    phone: Optional[str] = Field("", description="手机号")
    
    # 头像URL
    avatar: Optional[str] = Field("", description="头像URL")

    # 描述
    description: Optional[str] = Field("", description="描述信息")

    # 最后一次修改密码时间
    pwd_reset_time: Optional[datetime] = Field(None, description="最后一次修改密码时间")

    # 密码是否已过期
    pwd_expired: Optional[bool] = Field(False, description="密码是否已过期")

    # 注册日期
    registration_date: Optional[date] = Field(None, description="注册日期")

    # 部门ID
    dept_id: Optional[int] = Field(None, description="部门ID")

    # 部门名称
    dept_name: str = Field("", description="部门名称")

    # 权限码集合 - 🚨 解决操作列显示问题的关键字段
    permissions: Set[str] = Field(default_factory=set, description="权限码集合")

    # 角色编码集合
    roles: Set[str] = Field(default_factory=set, description="角色编码集合")

    # 角色名称列表
    role_names: List[str] = Field(default_factory=list, description="角色名称列表")
    
    def __str__(self) -> str:
        return f"UserInfo(id={self.id}, username='{self.username}', permissions_count={len(self.permissions)})"
    
    def has_permission(self, permission: str) -> bool:
        """检查是否拥有指定权限"""
        return permission in self.permissions

    def has_any_permission(self, permission_list: List[str]) -> bool:
        """检查是否拥有任意一个权限"""
        return any(perm in self.permissions for perm in permission_list)

    def is_super_admin(self) -> bool:
        """检查是否为超级管理员"""
        return "super_admin" in self.roles or self.id == 1