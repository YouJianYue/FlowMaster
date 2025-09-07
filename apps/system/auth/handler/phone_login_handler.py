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
            
            # 获取用户数据
            user_data = await self._get_user_by_phone(request.phone)
            
            # 执行认证并生成令牌
            login_resp = await AbstractLoginHandler.authenticate(user_data, client_info)
            
            # 后置处理
            await AbstractLoginHandler.post_login(self.current_user_context, login_resp, extra_info)
            
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
    
    async def _get_user_by_phone(self, phone: str) -> Dict[str, Any]:
        """
        根据手机号获取用户信息
        
        Args:
            phone: 手机号码
            
        Returns:
            Dict[str, Any]: 用户数据
        """
        # TODO: 实现数据库查询
        # 这里返回模拟数据
        if phone == "13800138000":
            return {
                "id": 2,
                "username": "user_phone",
                "nickname": "手机用户",
                "email": None,
                "phone": phone,
                "avatar": None,
                "status": 1,  # 启用状态
                "dept_id": None,
                "tenant_id": 1
            }
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="手机号未注册"
        )
    
    @property
    def current_user_context(self):
        """获取当前用户上下文"""
        from apps.common.context.user_context_holder import UserContextHolder
        return UserContextHolder.get_context()