# -*- coding: utf-8 -*-

"""
账号密码登录处理器 - 对应参考项目的AccountLoginHandler
"""

from typing import Dict, Any
from apps.system.auth.handler.abstract_login_handler import AbstractLoginHandler
from apps.system.auth.enums.auth_enums import AuthTypeEnum
from apps.common.config.exception.global_exception_handler import BadRequestException, BusinessException
from apps.system.auth.model.req.login_req import AccountLoginReq
from apps.system.auth.model.resp.auth_resp import LoginResp
from apps.system.auth.config.jwt_config import password_config
from apps.system.core.model.entity.client_entity import ClientEntity
from apps.system.core.model.entity.user_entity import UserEntity


class AccountLoginHandler(AbstractLoginHandler):
    """账号密码登录处理器"""

    def get_auth_type(self) -> AuthTypeEnum:
        """获取认证类型"""
        return AuthTypeEnum.ACCOUNT

    async def login(self, request: AccountLoginReq, client_info: Dict[str, Any],
                    extra_info: Dict[str, Any]) -> LoginResp:
        """
        执行账号密码登录

        Args:
            request: 账号登录请求
            client_info: 客户端信息
            extra_info: 额外信息

        Returns:
            LoginResp: 登录响应
        """
        try:
            # 前置处理
            await AbstractLoginHandler.pre_login(request, client_info, extra_info)

            # 验证用户凭据，获取UserEntity
            user = await self._authenticate_user(request.username, request.password)

            # 获取ClientEntity（临时使用字典创建对象，后续应该从数据库查询）
            client = await self._get_client_entity(client_info)

            # 执行认证并生成令牌
            login_resp = await AbstractLoginHandler.authenticate(user, client)

            # 获取当前用户上下文进行后置处理
            from apps.common.context.user_context_holder import UserContextHolder
            current_user_context = UserContextHolder.get_context()

            # 后置处理
            await AbstractLoginHandler.post_login(current_user_context, login_resp, extra_info)

            return login_resp

        except BadRequestException:
            # 业务异常(如验证码错误)直接向上抛出
            await self._log_login_failure(request.username, "认证失败", extra_info)
            raise
        except Exception as e:
            # 记录登录失败日志
            await self._log_login_failure(request.username, str(e), extra_info)
            raise BusinessException(f"登录失败: {str(e)}")

    async def _authenticate_user(self, username: str, password: str) -> 'UserEntity':
        """
        验证用户凭据

        Args:
            username: 用户名
            password: 密码 (RSA加密或明文)

        Returns:
            UserEntity: 用户实体对象
        """

        # RSA解密密码
        plain_password = self._decrypt_password(password)

        # 从数据库查询用户实体
        user = await self._get_user_by_username(username)

        if not user:
            raise BadRequestException("用户名或密码错误")

        # 验证密码
        if not password_config.verify_password(plain_password, user.password):
            raise BadRequestException("用户名或密码错误")

        return user

    async def _get_user_by_username(self, username: str) -> 'UserEntity':
        """
        根据用户名获取用户实体

        Args:
            username: 用户名

        Returns:
            UserEntity: 用户实体，未找到返回None
        """
        from apps.system.core.model.entity.user_entity import UserEntity
        from apps.common.config.database.database_session import DatabaseSession
        from sqlalchemy import select

        async with DatabaseSession.get_session_context() as session:
            stmt = select(UserEntity).where(UserEntity.username == username)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def _get_client_entity(self, client_info: Dict[str, Any]) -> 'ClientEntity':
        """
        获取客户端实体

        Args:
            client_info: 客户端信息字典

        Returns:
            ClientEntity: 客户端实体
        """
        from apps.common.config.database.database_session import DatabaseSession
        from sqlalchemy import select

        client_id = client_info.get('client_id')
        if not client_id:
            raise BadRequestException("缺少客户端ID")

        async with DatabaseSession.get_session_context() as session:
            stmt = select(ClientEntity).where(ClientEntity.client_id == client_id)
            result = await session.execute(stmt)
            client = result.scalar_one_or_none()

            if not client:
                raise BadRequestException("客户端不存在")

            # 检查客户端状态
            if not client.is_enabled():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="客户端已禁用"
                )

            return client

    def _decrypt_password(self, password: str) -> str:
        """
        解密密码

        Args:
            password: RSA加密的密码或明文密码

        Returns:
            str: 解密后的密码
        """
        try:
            # 尝试RSA解密
            from apps.common.util.secure_utils import SecureUtils
            from apps.common.config.rsa_properties import RsaProperties

            # 检查是否配置了RSA密钥
            if not RsaProperties.PRIVATE_KEY:
                print("⚠️  开发模式：未配置RSA私钥，将密码视为明文处理")
                # 开发环境下，如果是明文密码直接返回
                if len(password) <= 32 and not any(c in password for c in '+/='):
                    return password

            # 执行RSA解密 - 完全复刻参考项目的调用方式
            decrypted_password = SecureUtils.decrypt_password_by_rsa_private_key(password, "密码解密失败")
            return decrypted_password

        except Exception as e:
            print(f"⚠️  RSA解密失败: {e}")
            # 解密失败，尝试作为明文密码处理（开发环境兼容）
            if len(password) <= 32 and not any(c in password for c in '+/='):
                print("🔧 将密码视为明文处理")
                return password

            # 如果不像明文密码，抛出异常
            raise BadRequestException("密码解密失败，请检查密码格式")

    async def _log_login_failure(self, username: str, reason: str, extra_info: Dict[str, Any]):
        """记录登录失败日志"""
        # TODO: 实现登录失败日志记录
        print(f"登录失败 - 用户名: {username}, 原因: {reason}, 额外信息: {extra_info}")
        pass
