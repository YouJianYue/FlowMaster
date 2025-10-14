# -*- coding: utf-8 -*-

"""
WebSocket 管理器

参考项目的实时消息通知功能
"""

from fastapi import WebSocket
from typing import Dict, List

from apps.common.config.logging.logging_config import get_logger

logger = get_logger(__name__)


class WebSocketManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        # 存储活跃连接：{token: websocket}
        self.active_connections: Dict[str, WebSocket] = {}
        # 存储用户连接：{user_id: [tokens]}
        self.user_connections: Dict[int, List[str]] = {}

    async def connect(self, websocket: WebSocket, token: str, user_id: int):
        """接受WebSocket连接"""
        await websocket.accept()

        # 存储连接
        self.active_connections[token] = websocket

        # 存储用户连接映射
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(token)

        logger.info(f"WebSocket connected: user_id={user_id}, token={token[:8]}...")

    def disconnect(self, token: str, user_id: int):
        """断开WebSocket连接"""
        # 移除连接
        if token in self.active_connections:
            del self.active_connections[token]

        # 移除用户连接映射
        if user_id in self.user_connections:
            if token in self.user_connections[user_id]:
                self.user_connections[user_id].remove(token)

            # 如果用户没有活跃连接，移除用户记录
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

        logger.info(f"WebSocket disconnected: user_id={user_id}, token={token[:8]}...")

    async def send_personal_message(self, token: str, message: str):
        """发送个人消息"""
        if token in self.active_connections:
            try:
                await self.active_connections[token].send_text(message)
                return True
            except Exception as e:
                logger.error(f"Failed to send message to token {token[:8]}: {e}")
                # 连接可能已断开，清理连接
                if token in self.active_connections:
                    del self.active_connections[token]
                return False
        return False

    async def send_message_to_user(self, user_id: int, message: str):
        """发送消息给指定用户的所有连接"""
        if user_id not in self.user_connections:
            return False

        tokens = self.user_connections[user_id].copy()  # 复制列表避免迭代时修改
        success_count = 0

        for token in tokens:
            if await self.send_personal_message(token, message):
                success_count += 1

        return success_count > 0

    async def broadcast(self, message: str):
        """广播消息给所有连接"""
        if not self.active_connections:
            return

        tokens = list(self.active_connections.keys())  # 复制列表
        for token in tokens:
            await self.send_personal_message(token, message)

    def get_connection_count(self) -> int:
        """获取活跃连接数"""
        return len(self.active_connections)

    def get_user_count(self) -> int:
        """获取在线用户数"""
        return len(self.user_connections)


# 全局WebSocket管理器实例
websocket_manager = WebSocketManager()


class WebSocketUtils:
    """
    WebSocket工具类 - 一比一复刻参考项目的WebSocketUtils

    参考：top.continew.starter.messaging.websocket.util.WebSocketUtils
    """

    @staticmethod
    def send_message(token_or_message: str, message: str = None) -> bool:
        """
        发送WebSocket消息 - 一比一复刻参考项目API

        支持两种调用方式：
        1. sendMessage(token, message) - 发送给指定token的连接
        2. sendMessage(message) - 广播给所有在线用户

        参考实现：
        - WebSocketUtils.sendMessage(token, "1")
        - WebSocketUtils.sendMessage("1")

        Args:
            token_or_message: token或消息内容
            message: 消息内容（可选）

        Returns:
            bool: 发送是否成功
        """
        import asyncio

        # 判断调用方式
        if message is None:
            # 单参数调用 - 广播模式
            broadcast_message = token_or_message
            try:
                asyncio.create_task(websocket_manager.broadcast(broadcast_message))
                return True
            except Exception as e:
                logger.error(f"Failed to broadcast message: {e}")
                return False
        else:
            # 双参数调用 - 指定token发送
            token = token_or_message
            try:
                asyncio.create_task(
                    websocket_manager.send_personal_message(token, message)
                )
                return True
            except Exception as e:
                logger.error(f"Failed to send message to token {token[:8]}: {e}")
                return False

    @staticmethod
    async def send_message_to_user(user_id: int, message: str) -> bool:
        """
        发送消息到指定用户（扩展功能，非参考项目API）

        Args:
            user_id: 用户ID
            message: 消息内容

        Returns:
            bool: 发送是否成功
        """
        return await websocket_manager.send_message_to_user(user_id, message)

    @staticmethod
    def get_online_count() -> dict:
        """
        获取在线统计信息

        Returns:
            dict: 在线统计信息
        """
        return {
            "connections": websocket_manager.get_connection_count(),
            "users": websocket_manager.get_user_count()
        }