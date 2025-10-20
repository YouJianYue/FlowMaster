# -*- coding: utf-8 -*-

"""
第三方登录处理器 - 对应参考项目的SocialLoginHandler
"""

from typing import Dict, Any
from fastapi import HTTPException, status, Request
from apps.system.auth.handler.abstract_login_handler import AbstractLoginHandler
from apps.system.auth.enums.auth_enums import AuthTypeEnum, SocialSourceEnum
from apps.system.auth.model.req.login_req import SocialLoginReq
from apps.system.auth.model.resp.auth_resp import LoginResp
from apps.common.config.exception.global_exception_handler import BadRequestException, BusinessException


class SocialLoginHandler(AbstractLoginHandler):
    """第三方登录处理器"""
    
    def get_auth_type(self) -> AuthTypeEnum:
        """获取认证类型"""
        return AuthTypeEnum.SOCIAL
    
    async def login(self, request: SocialLoginReq, client: 'ClientResp', http_request: Request) -> LoginResp:
        """
        执行第三方登录

        Args:
            request: 第三方登录请求
            client: 客户端信息
            http_request: HTTP请求对象

        Returns:
            LoginResp: 登录响应
        """
        try:
            # 前置处理
            await self.pre_login(request, client, http_request)

            # 获取第三方用户信息
            social_user_info = await self._get_social_user_info(request.source, request.code, request.state)

            # 查找或创建本地用户，返回UserEntity
            user = await self._find_or_create_user(social_user_info, request.source)

            # 执行认证并生成令牌
            login_resp = await AbstractLoginHandler.authenticate(user, client, http_request)

            # 后置处理
            await self.post_login(request, client, http_request)

            return login_resp

        except HTTPException:
            # 记录登录失败日志（TODO: 实现登录日志记录）
            raise
        except Exception as e:
            # 记录登录失败日志（TODO: 实现登录日志记录）
            raise BusinessException(f"第三方登录失败: {str(e)}")
    
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
    
    async def _find_or_create_user(self, social_user_info: Dict[str, Any], source: str) -> 'UserEntity':
        """
        查找或创建本地用户

        一比一复刻参考项目SocialLoginHandler.login()的用户查找/创建逻辑

        Args:
            social_user_info: 第三方用户信息
            source: 第三方平台

        Returns:
            UserEntity: 本地用户实体
        """
        import json
        import re
        import uuid
        from datetime import datetime
        from sqlalchemy import select
        from apps.system.auth.service.user_social_service import UserSocialService
        from apps.system.core.model.entity.user_entity import UserEntity
        from apps.system.core.service.role_service import RoleService
        from apps.system.core.service.user_role_service import UserRoleService
        from apps.common.config.database.database_session import DatabaseSession
        from apps.common.enums.dis_enable_status_enum import DisEnableStatusEnum
        from apps.common.enums.gender_enum import GenderEnum

        # 一比一复刻参考项目：查找是否已绑定
        open_id = social_user_info.get("open_id")
        user_social = await UserSocialService.get_by_source_and_open_id(source, open_id)

        if user_social is None:
            # 一比一复刻参考项目：如未绑定则自动注册新用户
            async with DatabaseSession.get_session_context() as db:
                # 获取当前租户ID - 从租户上下文中获取
                # 如果前端传递了X-Tenant-Code，租户中间件已经设置到上下文中
                # 如果没有传递，使用默认租户ID=0
                from apps.common.context.tenant_context_holder import TenantContextHolder
                current_tenant_id = TenantContextHolder.getTenantId()
                if current_tenant_id is None:
                    current_tenant_id = 0  # 默认租户

                # 1. 生成用户名和昵称
                username = social_user_info.get("username", "")
                nickname = social_user_info.get("nickname", "")

                # 检查用户名是否已存在或不合规
                existing_user_stmt = select(UserEntity).where(UserEntity.username == username)
                result = await db.execute(existing_user_stmt)
                existing_user = result.scalar_one_or_none()

                # 如果用户名已存在或不合规（不符合正则），生成随机用户名
                random_str = ''.join([chr(ord('a') + i % 26) for i in range(5)])
                username_valid = bool(re.match(r"^[a-zA-Z0-9_-]{4,16}$", username))
                
                if existing_user or not username_valid:
                    username = random_str + str(uuid.uuid4().hex[:8])

                # 昵称不合规则生成随机昵称
                nickname_valid = bool(re.match(r"^[\u4e00-\u9fa5a-zA-Z0-9_-]{1,30}$", nickname))
                if not nickname_valid:
                    nickname = source.lower() + random_str

                # 2. 创建新用户
                new_user = UserEntity()
                new_user.username = username
                new_user.nickname = nickname

                # 设置性别 - 数据库gender字段是tinyint类型，需要整数值
                # 0=未知, 1=男, 2=女
                gender_mapping = {
                    "MALE": 1,
                    "FEMALE": 2
                }
                raw_gender = social_user_info.get("raw_user_info", {}).get("gender")
                new_user.gender = gender_mapping.get(raw_gender, 0)  # 默认未知

                new_user.avatar = social_user_info.get("avatar", "")
                new_user.password = ""  # 第三方登录用户没有密码
                new_user.dept_id = 1  # SystemConstants.SUPER_DEPT_ID
                new_user.status = 1  # 1=启用, 2=禁用（数据库status字段是tinyint类型）
                new_user.tenant_id = current_tenant_id  # 从租户上下文获取（0=默认租户）

                db.add(new_user)
                await db.flush()  # 获取新用户ID
                user_id = new_user.id

                # 3. 分配普通用户角色
                role_service = RoleService()
                general_role = await role_service.get_role_by_code("general")

                if general_role:
                    user_role_service = UserRoleService()
                    await user_role_service.assign_users_to_role(general_role.id, [user_id])

                # 4. 创建UserSocial关联
                from apps.system.auth.model.entity.user_social_entity import UserSocialEntity

                user_social = UserSocialEntity()
                user_social.user_id = user_id
                user_social.source = source
                user_social.open_id = social_user_info["open_id"]
                user_social.meta_json = json.dumps(social_user_info, ensure_ascii=False)
                user_social.last_login_time = datetime.now()
                user_social.tenant_id = current_tenant_id  # 与用户使用相同租户ID

                db.add(user_social)
                await db.commit()

                # 刷新user对象以获取最新状态
                await db.refresh(new_user)

                # 返回用户实体
                return new_user
        else:
            # 一比一复刻参考项目：如果已绑定，获取用户信息
            async with DatabaseSession.get_session_context() as db:
                user_stmt = select(UserEntity).where(UserEntity.id == user_social.user_id)
                result = await db.execute(user_stmt)
                user = result.scalar_one_or_none()

                if not user:
                    raise BadRequestException("关联用户不存在")

                # 更新UserSocial的meta_json和last_login_time
                user_social.meta_json = json.dumps(social_user_info, ensure_ascii=False)
                user_social.last_login_time = datetime.now()
                await UserSocialService.save_or_update(user_social)

                # 刷新user对象以获取最新状态
                await db.refresh(user)

                # 返回用户实体
                return user

    
    @property
    def current_user_context(self):
        """获取当前用户上下文"""
        from apps.common.context.user_context_holder import UserContextHolder
        return UserContextHolder.get_context()