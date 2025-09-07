# -*- coding: utf-8 -*-

"""
账号密码登录处理器 - 对应参考项目的AccountLoginHandler
"""

from typing import Dict, Any
from fastapi import HTTPException, status
from apps.system.auth.handler.abstract_login_handler import AbstractLoginHandler
from apps.system.auth.enums.auth_enums import AuthTypeEnum
from apps.system.auth.model.req.login_req import AccountLoginReq
from apps.system.auth.model.resp.auth_resp import LoginResp
from apps.system.auth.config.jwt_config import password_config


class AccountLoginHandler(AbstractLoginHandler):
    """账号密码登录处理器"""
    
    def get_auth_type(self) -> AuthTypeEnum:
        """获取认证类型"""
        return AuthTypeEnum.ACCOUNT
    
    async def login(self, request: AccountLoginReq, client_info: Dict[str, Any], extra_info: Dict[str, Any]) -> LoginResp:
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
            
            # 验证用户凭据
            user_data = await self._authenticate_user(request.username, request.password)
            
            # 执行认证并生成令牌
            login_resp = await AbstractLoginHandler.authenticate(user_data, client_info)
            
            # 后置处理
            await AbstractLoginHandler.post_login(self.current_user_context, login_resp, extra_info)
            
            return login_resp
            
        except HTTPException:
            # 记录登录失败日志
            await self._log_login_failure(request.username, "密码错误", extra_info)
            raise
        except Exception as e:
            # 记录登录失败日志
            await self._log_login_failure(request.username, str(e), extra_info)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"登录失败: {str(e)}"
            )
    
    async def _authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        """
        验证用户凭据
        
        Args:
            username: 用户名
            password: 密码 (RSA加密或明文)
            
        Returns:
            Dict[str, Any]: 用户数据
        """
        # RSA解密密码
        plain_password = self._decrypt_password(password)
        
        # 模拟从数据库查询用户
        # TODO: 实际实现时应该从UserService或Repository获取
        user_data = await self._get_user_by_username(username)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        # 验证密码
        if not password_config.verify_password(plain_password, user_data.get('password_hash')):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        return user_data
    
    async def _get_user_by_username(self, username: str) -> Dict[str, Any]:
        """
        根据用户名获取用户信息
        
        Args:
            username: 用户名
            
        Returns:
            Dict[str, Any]: 用户数据，如果不存在返回None
        """
        # TODO: 实现数据库查询
        # 这里返回模拟数据，实际应该查询数据库
        if username == "admin":
            return {
                "id": 1,
                "username": "admin",
                "nickname": "管理员",
                "email": "admin@example.com",
                "phone": None,
                "avatar": None,
                "password_hash": password_config.get_password_hash("admin123"),  # 修改为admin123
                "status": 1,  # 启用状态
                "dept_id": None,
                "tenant_id": 1
            }
        
        return None
    
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
                    
            return SecureUtils.decrypt_password_by_rsa_private_key(
                encrypted_password=password,
                error_msg="密码解密失败"
            )
            
        except (ValueError, TypeError, Exception) as e:
            print(f"🔓 RSA解密失败，尝试明文密码处理: {str(e)}")
            
            # 开发环境兜底：如果RSA解密失败，检查是否为简单明文密码
            if len(password) <= 32 and password.isalnum():
                print(f"💡 检测到可能的明文密码: {password}")
                return password
            
            # 如果密码看起来像Base64，尝试简单的解码（但这不是RSA解密）
            try:
                import base64
                decoded = base64.b64decode(password.encode()).decode()
                print(f"💡 Base64解码成功: {decoded}")
                return decoded
            except:
                pass
                
            # 最后尝试：原样返回（可能前端没有加密）
            print(f"⚠️  密码解密完全失败，原样返回")
            return password
    
    @property
    def current_user_context(self):
        """获取当前用户上下文"""
        from apps.common.context.user_context_holder import UserContextHolder
        return UserContextHolder.get_context()