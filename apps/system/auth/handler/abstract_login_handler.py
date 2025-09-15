# -*- coding: utf-8 -*-

"""
抽象登录处理器
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from fastapi import HTTPException, status
from apps.system.auth.enums.auth_enums import AuthTypeEnum
from apps.system.auth.model.req.login_req import LoginReq
from apps.system.auth.model.resp.auth_resp import LoginResp, UserInfoResp
from apps.system.auth.config.jwt_config import jwt_utils
from apps.common.context.user_context import UserContext
from apps.common.context.user_context_holder import UserContextHolder
from apps.common.enums.dis_enable_status_enum import DisEnableStatusEnum


class AbstractLoginHandler(ABC):
    """抽象登录处理器"""

    @abstractmethod
    async def login(self, request: LoginReq, client_info: Dict[str, Any], extra_info: Dict[str, Any]) -> LoginResp:
        """
        执行登录逻辑
        
        Args:
            request: 登录请求
            client_info: 客户端信息
            extra_info: 额外信息 (IP、浏览器等)
            
        Returns:
            LoginResp: 登录响应
        """
        pass

    @abstractmethod
    def get_auth_type(self) -> AuthTypeEnum:
        """获取认证类型"""
        pass

    @staticmethod
    async def pre_login(request: LoginReq, _client_info: Dict[str, Any], _extra_info: Dict[str, Any]):
        """
        登录前置处理
        """
        # 🚨 临时禁用验证码校验，方便测试权限系统
        print("🔧 [测试模式] 跳过验证码校验")
        # await AbstractLoginHandler._validate_captcha(request)

    @staticmethod
    async def post_login(user_context: UserContext, _login_resp: LoginResp, extra_info: Dict[str, Any]):
        """
        登录后置处理
        """
        # 记录登录日志
        await AbstractLoginHandler._log_login_success(user_context, extra_info)

    @staticmethod
    def check_user_status(user_data: Dict[str, Any]):
        """
        检查用户状态
        
        Args:
            user_data: 用户数据
        """
        # 检查用户是否被禁用
        if user_data.get('status') == DisEnableStatusEnum.DISABLE.value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="账号已被禁用，请联系管理员"
            )

        # 检查账号是否过期等其他状态检查...
        # TODO: 添加部门状态检查（需要实现DeptService后）

    @staticmethod
    async def authenticate(user_data: Dict[str, Any], client_info: Dict[str, Any]) -> LoginResp:
        """
        执行认证，生成令牌
        
        Args:
            user_data: 用户数据
            client_info: 客户端信息
            
        Returns:
            LoginResp: 登录响应
        """
        # 检查用户状态
        AbstractLoginHandler.check_user_status(user_data)

        # 创建用户上下文 (这里简化处理，实际应该获取完整的权限和角色信息)
        user_context = UserContext(
            id=user_data['id'],
            username=user_data['username'],
            nickname=user_data.get('nickname'),
            email=user_data.get('email'),
            phone=user_data.get('phone'),
            avatar=user_data.get('avatar'),
            dept_id=user_data.get('dept_id'),
            tenant_id=user_data.get('tenant_id', 1),  # 默认租户
            client_type=client_info.get('client_type'),
            client_id=client_info.get('client_id'),
            permissions=set(),  # TODO: 从数据库获取
            role_codes=set(),  # TODO: 从数据库获取
            roles=set()  # TODO: 从数据库获取
        )

        # 设置用户上下文
        UserContextHolder.set_context(user_context)

        # 生成JWT令牌
        token_data = {
            "user_id": user_context.id,
            "username": user_context.username,
            "tenant_id": user_context.tenant_id,
            "client_id": user_context.client_id
        }

        access_token = jwt_utils.create_access_token(token_data)
        refresh_token = jwt_utils.create_refresh_token({"user_id": user_context.id})

        # 构造用户信息响应
        user_info = UserInfoResp(
            id=user_context.id,
            username=user_context.username,
            nickname=user_context.nickname,
            avatar=user_context.avatar,
            email=user_context.email,
            phone=user_context.phone,
            permissions=list(user_context.permissions),
            roles=list(user_context.role_codes),
            is_super_admin=user_context.is_super_admin_user(),
            is_pwd_expired=user_context.is_password_expired()
        )

        return LoginResp(
            token=access_token,              # 与参考项目保持一致
            tenant_id=user_context.tenant_id, # 与参考项目保持一致
            access_token=access_token,        # 向后兼容
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=jwt_utils.config.access_token_expire_minutes * 60,
            user_info=user_info
        )

    @staticmethod
    async def _validate_captcha(request: LoginReq):
        """验证码校验"""
        # 导入验证码缓存（避免循环导入）
        from apps.common.controller.captcha_controller import captcha_cache
        from datetime import datetime
        
        # 只对账号登录进行验证码校验（参考项目中的逻辑）
        from apps.system.auth.model.req.login_req import AccountLoginReq
        if not isinstance(request, AccountLoginReq):
            return
            
        # 如果没有提供验证码信息，则跳过验证（兼容某些客户端）
        if not hasattr(request, 'uuid') or not request.uuid:
            return
            
        if not hasattr(request, 'captcha') or not request.captcha:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请输入验证码"
            )
            
        # 清理过期验证码
        current_time = datetime.now()
        expired_keys = [
            key for key, data in captcha_cache.items()
            if current_time > data['expire_time']
        ]
        for key in expired_keys:
            del captcha_cache[key]
            
        # 检查验证码UUID是否存在
        if request.uuid not in captcha_cache:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="验证码已过期或不存在，请重新获取"
            )
            
        cached_data = captcha_cache[request.uuid]
        
        # 验证验证码（忽略大小写）
        if request.captcha.lower() != cached_data['code']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="验证码错误，请重新输入"
            )
            
        # 验证成功，删除验证码（一次性使用）
        del captcha_cache[request.uuid]

    @staticmethod
    async def _log_login_success(_user_context: UserContext, _extra_info: Dict[str, Any]):
        """记录登录成功日志"""
        # TODO: 实现登录日志记录
        pass

    @staticmethod
    async def _log_login_failure(_username: str, _reason: str, _extra_info: Dict[str, Any]):
        """记录登录失败日志"""
        # TODO: 实现登录失败日志记录
        pass
