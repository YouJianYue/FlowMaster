# -*- coding: utf-8 -*-
"""
消息服务接口

一比一复刻参考项目 MessageService.java
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from apps.system.core.model.resp.message_unread_resp import MessageUnreadResp


class MessageService(ABC):
    """
    消息服务接口

    一比一复刻参考项目 MessageService.java
    """

    @abstractmethod
    async def count_unread_by_user_id(self, user_id: int, is_detail: Optional[bool] = False) -> MessageUnreadResp:
        """
        查询用户未读消息数量

        一比一复刻: countUnreadByUserId(Long userId, Boolean isDetail)

        Args:
            user_id: 用户ID
            is_detail: 是否查询详情

        Returns:
            MessageUnreadResp: 未读消息响应
        """
        pass

    @abstractmethod
    async def read_message(self, ids: Optional[List[int]], user_id: int):
        """
        标记消息已读

        一比一复刻: readMessage(List<Long> ids, Long userId)

        参考实现：
        1. 查询当前用户的未读消息
        2. 标记指定消息为已读（如果ids为空则标记全部）
        3. 通过WebSocket推送更新后的未读数量

        Args:
            ids: 消息ID列表（可选，为None时标记全部未读消息）
            user_id: 用户ID
        """
        pass

    @abstractmethod
    async def add(self, title: str, content: str, message_type: str, user_id_list: Optional[List[str]] = None):
        """
        创建消息

        一比一复刻: add(MessageReq req, List<String> userIdList)

        参考实现：
        1. 创建消息记录
        2. 如果指定了用户列表，发送给指定用户
        3. 否则发送给所有用户
        4. 通过WebSocket通知相关用户

        Args:
            title: 消息标题
            content: 消息内容
            message_type: 消息类型
            user_id_list: 目标用户ID列表（可选，为None时发送给所有用户）
        """
        pass