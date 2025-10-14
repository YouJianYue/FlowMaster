# -*- coding: utf-8 -*-

"""
带自动时间序列化的基础响应模型
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, model_serializer


class BaseDatetimeResp(BaseModel):
    """
    带自动时间序列化的基础响应模型

    所有 datetime 类型字段会自动序列化为 "YYYY-MM-DD HH:MM:SS" 格式
    子类只需继承此类即可自动获得时间序列化功能
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

    @model_serializer(mode='wrap', when_used='json')
    def serialize_model(self, serializer, info):
        """
        模型序列化器 - 自动格式化所有 datetime 字段

        使用 model_serializer 而不是 field_serializer，
        这样可以统一处理模型中的所有 datetime 字段，
        子类不需要重复定义序列化器
        """
        data = serializer(self)

        # 遍历所有字段，格式化 datetime 类型
        for field_name, field_info in self.model_fields.items():
            # 获取字段值
            value = data.get(field_name)

            # 如果是 datetime 类型且不为 None，格式化为标准格式
            if isinstance(value, datetime):
                data[field_name] = value.strftime("%Y-%m-%d %H:%M:%S")

        return data
