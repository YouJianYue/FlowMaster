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
            login_resp = await AbstractLoginHandler.authenticate(user_data, client_info, http_request)
            
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
        # 根据不同平台获取用户信息
        if source == SocialSourceEnum.DINGTALK.value:
            # 钉钉OAuth
            from apps.system.auth.oauth.dingtalk_oauth import DingTalkOAuthClient

            dingtalk_client = DingTalkOAuthClient()
            user_info = await dingtalk_client.get_user_info(code)
            return user_info

        elif source == SocialSourceEnum.WECHAT.value:
            # 微信开放平台OAuth
            from apps.system.auth.oauth.wechat_oauth import WeChatOAuthClient

            wechat_client = WeChatOAuthClient()
            user_info = await wechat_client.get_user_info(code)
            return user_info

        elif source == SocialSourceEnum.GITEE.value:
            # Gitee OAuth
            # TODO: 实现Gitee OAuth用户信息获取
            return {
                "open_id": "123456",
                "username": "gitee_user",
                "nickname": "Gitee用户",
                "avatar": "https://gitee.com/avatar.jpg",
                "email": "user@gitee.com",
                "source": source,
            }

        elif source == SocialSourceEnum.GITHUB.value:
            # GitHub OAuth
            # TODO: 实现GitHub OAuth用户信息获取
            return {
                "open_id": "654321",
                "username": "github_user",
                "nickname": "GitHub用户",
                "avatar": "https://github.com/avatar.jpg",
                "email": "user@github.com",
                "source": source,
            }

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的第三方平台: {source}",
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
        # TODO: 实现查找或创建用户的数据库逻辑
        # 参考Java项目的SocialLoginHandler实现:
        # 1. 根据source和open_id查询sys_user_social表
        # 2. 如果找到，返回关联的用户信息
        # 3. 如果没找到:
        #    - 根据username/email查找是否存在本地用户
        #    - 如果不存在，创建新用户并分配普通用户角色
        #    - 创建sys_user_social关联记录
        # 4. 更新UserSocial的meta_json和last_login_time

        # 暂时返回模拟数据作为骨架
        return {
            "id": 3,
            "username": social_user_info["username"],
            "nickname": social_user_info["nickname"],
            "email": social_user_info.get("email"),
            "phone": social_user_info.get("mobile"),
            "avatar": social_user_info.get("avatar"),
            "status": 1,  # 启用状态
            "dept_id": None,
            "tenant_id": 1,
            "social_source": source,
            "open_id": social_user_info["open_id"],
        }
    
    @property
    def current_user_context(self):
        """获取当前用户上下文"""
        from apps.common.context.user_context_holder import UserContextHolder
        return UserContextHolder.get_context()