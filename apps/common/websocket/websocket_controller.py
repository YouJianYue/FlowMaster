# -*- coding: utf-8 -*-

"""
WebSocket 路由控制器

完全复刻参考项目的 WebSocket 功能
"""

from fastapi import WebSocket, WebSocketDisconnect, Query, status
from fastapi.routing import APIRouter
import json
import logging

logger = logging.getLogger(__name__)

# 创建WebSocket路由
websocket_router = APIRouter()


@websocket_router.websocket("/websocket")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    """
    WebSocket端点 - 参考项目的 /websocket 路径

    Args:
        websocket: WebSocket连接
        token: JWT访问令牌
    """
    try:
        # 延迟导入，避免循环导入
        from apps.common.websocket.websocket_manager import websocket_manager
        from apps.system.auth.config.jwt_config import jwt_utils

        # 验证JWT令牌
        try:
            payload = jwt_utils.verify_token(token)
            user_id = payload.get("user_id")
            username = payload.get("username")

            if not user_id:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
                return

        except Exception as e:
            logger.warning(f"WebSocket authentication failed: {e}")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication failed")
            return

        # 建立连接
        await websocket_manager.connect(websocket, token, user_id)

        try:
            # 发送连接成功消息
            welcome_message = {
                "type": "connection",
                "status": "connected",
                "message": f"Welcome {username}!",
                "timestamp": jwt_utils.get_current_timestamp()
            }
            await websocket.send_text(json.dumps(welcome_message))

            # 保持连接并处理消息
            while True:
                try:
                    # 接收客户端消息
                    data = await websocket.receive_text()
                    logger.debug(f"Received WebSocket message from user {user_id}: {data}")

                    # 这里可以处理客户端发送的消息
                    # 比如心跳包、状态更新等
                    try:
                        message_data = json.loads(data)
                        message_type = message_data.get("type")

                        if message_type == "ping":
                            # 响应心跳包
                            pong_message = {
                                "type": "pong",
                                "timestamp": jwt_utils.get_current_timestamp()
                            }
                            await websocket.send_text(json.dumps(pong_message))

                    except json.JSONDecodeError:
                        # 忽略非JSON消息
                        pass

                except WebSocketDisconnect:
                    break
                except Exception as e:
                    logger.error(f"Error handling WebSocket message from user {user_id}: {e}")
                    break

        except WebSocketDisconnect:
            pass
        except Exception as e:
            logger.error(f"WebSocket connection error for user {user_id}: {e}")
        finally:
            # 清理连接
            websocket_manager.disconnect(token, user_id)

    except Exception as e:
        logger.error(f"WebSocket endpoint error: {e}")
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason="Internal server error")
        except:
            pass


# 可选：添加WebSocket状态查询接口
from fastapi import APIRouter

api_router = APIRouter(prefix="/websocket", tags=["WebSocket"])


@api_router.get("/status")
async def get_websocket_status():
    """
    获取WebSocket连接状态

    Returns:
        dict: WebSocket状态信息
    """
    # 延迟导入，避免循环导入
    from apps.common.websocket.websocket_manager import WebSocketUtils
    from apps.system.auth.config.jwt_config import jwt_utils

    return {
        "status": "active",
        "online_stats": WebSocketUtils.get_online_count(),
        "timestamp": jwt_utils.get_current_timestamp()
    }