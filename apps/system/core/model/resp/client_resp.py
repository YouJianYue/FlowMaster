# -*- coding: utf-8 -*-

"""
客户端响应模型 - 对应参考项目的ClientResp
"""

from typing import List
from pydantic import BaseModel, Field, ConfigDict
from apps.common.base.model.resp.base_detail_resp import BaseDetailResp
from apps.common.enums.dis_enable_status_enum import DisEnableStatusEnum


class ClientResponse(BaseDetailResp):
    """
    客户端响应参数
    
    对应Java响应: ClientResp
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    # 客户端 ID
    client_id: str = Field(description="客户端ID", examples=["ef51c9a3e9046c4f2ea45142c8a8344a"])
    
    # 客户端类型
    client_type: str = Field(description="客户端类型", examples=["WEB"])
    
    # 支持的认证类型列表
    auth_type: List[str] = Field(description="支持的认证类型", examples=[["ACCOUNT", "EMAIL", "PHONE"]])
    
    # Token最低活跃频率（单位：秒）
    active_timeout: int = Field(description="Token最低活跃频率(秒，-1表示不限制)", examples=[1800])
    
    # Token有效期（单位：秒）
    timeout: int = Field(description="Token有效期(秒，-1表示永不过期)", examples=[86400])
    
    # 状态
    status: DisEnableStatusEnum = Field(description="状态", examples=[DisEnableStatusEnum.ENABLE])


class ClientInfo(BaseModel):
    """
    客户端基本信息（用于内部传递）
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    client_id: str = Field(description="客户端ID")
    client_type: str = Field(description="客户端类型") 
    auth_type: List[str] = Field(description="支持的认证类型")
    active_timeout: int = Field(description="Token最低活跃频率")
    timeout: int = Field(description="Token有效期")
    status: DisEnableStatusEnum = Field(description="状态")
    
    def is_enabled(self) -> bool:
        """检查客户端是否启用"""
        return self.status == DisEnableStatusEnum.ENABLE
    
    def is_auth_type_supported(self, auth_type: str) -> bool:
        """检查是否支持指定的认证类型"""
        return auth_type in self.auth_type if self.auth_type else False