# -*- coding: utf-8 -*-

"""
用户信息响应模型 - 完全匹配参考项目的字段结构
使用Pydantic自动处理snake_case到camelCase转换
"""

from typing import List, Optional
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
                "deptName": "总办",
                "roles": ["super_admin"],
                "permissions": [
                    "system:menu:list",
                    "system:menu:create",
                    "system:menu:update", 
                    "system:menu:delete",
                    "system:user:list",
                    "system:user:create",
                    "system:user:update",
                    "system:user:delete"
                ]
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
    
    # 部门名称
    dept_name: str = Field("", description="部门名称")
    
    # 角色编码列表
    roles: List[str] = Field(default_factory=list, description="角色编码列表")
    
    # 权限码列表 - 🚨 解决操作列显示问题的关键字段
    permissions: List[str] = Field(default_factory=list, description="权限码列表")
    
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