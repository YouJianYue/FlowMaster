# -*- coding: utf-8 -*-

"""
WebSocket 管理器

参考项目的实时消息通知功能
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json

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
    """WebSocket工具类 - 参考项目的WebSocketUtils"""

    @staticmethod
    async def send_message(token: str, message: str) -> bool:
        """
        发送消息到指定token的连接

        Args:
            token: JWT token
            message: 消息内容

        Returns:
            bool: 发送是否成功
        """
        return await websocket_manager.send_personal_message(token, message)

    @staticmethod
    async def send_message_to_user(user_id: int, message: str) -> bool:
        """
        发送消息到指定用户

        Args:
            user_id: 用户ID
            message: 消息内容

        Returns:
            bool: 发送是否成功
        """
        return await websocket_manager.send_message_to_user(user_id, message)

    @staticmethod
    async def broadcast_message(message: str):
        """
        广播消息到所有连接

        Args:
            message: 消息内容
        """
        await websocket_manager.broadcast(message)

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