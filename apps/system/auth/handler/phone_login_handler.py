# -*- coding: utf-8 -*-

"""
手机登录处理器 - 对应参考项目的PhoneLoginHandler
"""

from typing import Dict, Any
from fastapi import HTTPException, status
from apps.system.auth.handler.abstract_login_handler import AbstractLoginHandler
from apps.system.auth.enums.auth_enums import AuthTypeEnum
from apps.system.auth.model.req.login_req import PhoneLoginReq
from apps.system.auth.model.resp.auth_resp import LoginResp


class PhoneLoginHandler(AbstractLoginHandler):
    """手机登录处理器"""
    
    def get_auth_type(self) -> AuthTypeEnum:
        """获取认证类型"""
        return AuthTypeEnum.PHONE
    
    async def login(self, request: PhoneLoginReq, client_info: Dict[str, Any], extra_info: Dict[str, Any]) -> LoginResp:
        """
        执行手机登录
        
        Args:
            request: 手机登录请求
            client_info: 客户端信息
            extra_info: 额外信息
            
        Returns:
            LoginResp: 登录响应
        """
        try:
            # 前置处理
            await AbstractLoginHandler.pre_login(request, client_info, extra_info)
            
            # 验证短信验证码
            await self._validate_sms_captcha(request.phone, request.captcha)
            
            # 获取用户实体
            user = await self._get_user_by_phone(request.phone)

            # 获取客户端实体
            client = await self._get_client_entity(client_info)

            # 执行认证并生成令牌
            login_resp = await AbstractLoginHandler.authenticate(user, client, http_request)

            # 获取当前用户上下文进行后置处理
            from apps.common.context.user_context_holder import UserContextHolder
            current_user_context = UserContextHolder.get_context()

            # 后置处理
            await AbstractLoginHandler.post_login(current_user_context, login_resp, extra_info)
            
            return login_resp
            
        except HTTPException:
            # 记录登录失败日志
            await self._log_login_failure(request.phone, "短信验证码错误", extra_info)
            raise
        except Exception as e:
            # 记录登录失败日志
            await self._log_login_failure(request.phone, str(e), extra_info)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"手机登录失败: {str(e)}"
            )
    
    async def _validate_sms_captcha(self, phone: str, captcha: str):
        """
        验证短信验证码
        
        Args:
            phone: 手机号码
            captcha: 验证码
        """
        # TODO: 实现短信验证码校验逻辑
        # 这里暂时跳过验证码校验
        pass
    
    async def _get_user_by_phone(self, phone: str) -> 'UserEntity':
        """
        根据手机号获取用户实体

        Args:
            phone: 手机号码

        Returns:
            UserEntity: 用户实体对象
        """
        from apps.system.core.model.entity.user_entity import UserEntity
        from apps.common.config.database.database_session import DatabaseSession
        from sqlalchemy import select

        async with DatabaseSession.get_session_context() as session:
            stmt = select(UserEntity).where(UserEntity.phone == phone)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="手机号未注册"
                )

            return user

    async def _get_client_entity(self, client_info: Dict[str, Any]) -> 'ClientEntity':
        """
        获取客户端实体

        Args:
            client_info: 客户端信息字典

        Returns:
            ClientEntity: 客户端实体
        """
        from apps.system.core.model.entity.client_entity import ClientEntity
        from apps.common.config.database.database_session import DatabaseSession
        from sqlalchemy import select

        client_id = client_info.get('client_id')
        if not client_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="缺少客户端ID"
            )

        async with DatabaseSession.get_session_context() as session:
            stmt = select(ClientEntity).where(ClientEntity.client_id == client_id)
            result = await session.execute(stmt)
            client = result.scalar_one_or_none()

            if not client:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="客户端不存在"
                )

            # 检查客户端状态
            if not client.is_enabled():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="客户端已禁用"
                )

            return client

    async def _log_login_failure(self, phone: str, reason: str, extra_info: Dict[str, Any]):
        """记录登录失败日志"""
        # TODO: 实现登录失败日志记录
        print(f"手机登录失败 - 手机号: {phone}, 原因: {reason}, 额外信息: {extra_info}")
        pass