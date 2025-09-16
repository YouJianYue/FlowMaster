# -*- coding: utf-8 -*-

"""
字典业务API接口
"""

from abc import ABC, abstractmethod
from typing import List
from pydantic import BaseModel


class LabelValueResponse(BaseModel):
    """标签值响应模型"""
    
    label: str
    value: str


class DictApi(ABC):
    """字典业务API接口"""
    
    @abstractmethod
    async def list_all(self) -> List[LabelValueResponse]:
        """
        查询字典列表
        
        Returns:
            字典列表（包含枚举字典列表）
        """
        pass