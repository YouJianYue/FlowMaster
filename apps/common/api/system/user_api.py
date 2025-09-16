# -*- coding: utf-8 -*-

"""
用户业务API接口
"""

from abc import ABC, abstractmethod
from typing import Optional


class UserApi(ABC):
    """用户业务API接口"""

    @abstractmethod
    async def get_nickname_by_id(self, user_id: int) -> Optional[str]:
        """
        根据ID查询昵称
        
        Args:
            user_id: 用户ID
            
        Returns:
            昵称
        """
        pass

    @abstractmethod
    async def reset_password(self, new_password: str, user_id: int) -> None:
        """
        重置密码
        
        Args:
            new_password: 新密码
            user_id: 用户ID
        """
        pass
