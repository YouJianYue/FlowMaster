# -*- coding: utf-8 -*-
"""
消息类型枚举

@author: continew-admin
@since: 2023/11/2 20:08
"""

from enum import IntEnum


class MessageTypeEnum(IntEnum):
    """消息类型枚举"""
    
    # 系统消息
    SYSTEM = 1
    # 安全消息
    SECURITY = 2
    
    @property 
    def description(self):
        """获取描述"""
        descriptions = {
            MessageTypeEnum.SYSTEM: "系统消息",
            MessageTypeEnum.SECURITY: "安全消息"
        }
        return descriptions.get(self, "未知")
    
    @property
    def color(self):
        """获取颜色"""
        colors = {
            MessageTypeEnum.SYSTEM: "primary",
            MessageTypeEnum.SECURITY: "warning"
        }
        return colors.get(self, "default")