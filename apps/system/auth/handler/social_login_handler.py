# -*- coding: utf-8 -*-

"""
第三方登录处理器 - 对应参考项目的SocialLoginHandler
"""

from typing import Dict, Any
from fastapi import HTTPException, status
from apps.system.auth.handler.abstract_login_handler import AbstractLoginHandler
from apps.system.auth.enums.auth_enums import AuthTypeEnum, SocialSourceEnum
from apps.system.auth.model.req.login_req import SocialLoginReq
from apps.system.auth.model.resp.auth_resp import LoginResp


class SocialLoginHandler(AbstractLoginHandler):
    """第三方登录处理器"""
    
    def get_auth_type(self) -> AuthTypeEnum:
        """获取认证类型"""
        return AuthTypeEnum.SOCIAL
    
    async def login(self, request: SocialLoginReq, client_info: Dict[str, Any], extra_info: Dict[str, Any]) -> LoginResp:
        """
        执行第三方登录
        
        Args:
            request: 第三方登录请求
            client_info: 客户端信息
            extra_info: 额外信息
            
        Returns:
            LoginResp: 登录响应
        """
        try:
            # 前置处理
            await AbstractLoginHandler.pre_login(request, client_info, extra_info)
            
            # 获取第三方用户信息
            social_user_info = await self._get_social_user_info(request.source, request.code, request.state)
            
            # 查找或创建本地用户
            user_data = await self._find_or_create_user(social_user_info, request.source)
            
            # 执行认证并生成令牌
            login_resp = await AbstractLoginHandler.authenticate(user_data, client_info)
            
            # 后置处理
            await AbstractLoginHandler.post_login(self.current_user_context, login_resp, extra_info)
            
            return login_resp
            
        except HTTPException:
            # 记录登录失败日志
            await self._log_login_failure(f"{request.source}_user", "第三方登录失败", extra_info)
            raise
        except Exception as e:
            # 记录登录失败日志
            await self._log_login_failure(f"{request.source}_user", str(e), extra_info)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"第三方登录失败: {str(e)}"
            )
    
    async def _get_social_user_info(self, source: str, code: str, state: str) -> Dict[str, Any]:
        """
        获取第三方用户信息
        
        Args:
            source: 第三方平台
            code: 授权码
            state: 状态码
            
        Returns:
            Dict[str, Any]: 第三方用户信息
        """
        # TODO: 实现各种第三方平台的OAuth获取用户信息
        # 这里返回模拟数据
        if source == SocialSourceEnum.GITEE.value:
            return {
                "social_id": "123456",
                "username": "gitee_user",
                "nickname": "Gitee用户",
                "avatar": "https://gitee.com/avatar.jpg",
                "email": "user@gitee.com",
                "source": source
            }
        elif source == SocialSourceEnum.GITHUB.value:
            return {
                "social_id": "654321",
                "username": "github_user", 
                "nickname": "GitHub用户",
                "avatar": "https://github.com/avatar.jpg",
                "email": "user@github.com",
                "source": source
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的第三方平台: {source}"
            )
    
    async def _find_or_create_user(self, social_user_info: Dict[str, Any], source: str) -> Dict[str, Any]:
        """
        查找或创建本地用户
        
        Args:
            social_user_info: 第三方用户信息
            source: 第三方平台
            
        Returns:
            Dict[str, Any]: 本地用户数据
        """
        # TODO: 实现查找或创建用户的逻辑
        # 1. 先根据第三方ID查找是否已绑定本地用户
        # 2. 如果没有，根据邮箱查找是否存在本地用户进行绑定
        # 3. 如果都没有，创建新用户
        
        # 这里返回模拟数据
        return {
            "id": 3,
            "username": social_user_info["username"],
            "nickname": social_user_info["nickname"],
            "email": social_user_info.get("email"),
            "phone": None,
            "avatar": social_user_info.get("avatar"),
            "status": 1,  # 启用状态
            "dept_id": None,
            "tenant_id": 1,
            "social_source": source,
            "social_id": social_user_info["social_id"]
        }
    
    @property
    def current_user_context(self):
        """获取当前用户上下文"""
        from apps.common.context.user_context_holder import UserContextHolder
        return UserContextHolder.get_context()