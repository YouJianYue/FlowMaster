# -*- coding: utf-8 -*-

"""
抽象登录处理器
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, Any
from fastapi import HTTPException, status, Request
from apps.system.auth.enums.auth_enums import AuthTypeEnum
from apps.system.auth.model.req.login_req import LoginReq
from apps.system.auth.model.resp.auth_resp import LoginResp, UserInfoResp
from apps.system.auth.config.jwt_config import jwt_utils
from apps.common.context.user_context import UserContext
from apps.common.context.user_context_holder import UserContextHolder
from apps.common.enums.dis_enable_status_enum import DisEnableStatusEnum

if TYPE_CHECKING:
    from apps.system.core.model.resp.client_resp import ClientResp


class AbstractLoginHandler(ABC):
    """抽象登录处理器 - 一比一复刻参考项目LoginHandler接口"""

    @abstractmethod
    async def login(self, request: LoginReq, client: 'ClientResp', http_request: Request) -> LoginResp:
        """
        登录 - 一比一复刻参考项目LoginHandler接口

        Args:
            request: 登录请求参数
            client: 客户端信息
            http_request: HTTP请求对象

        Returns:
            LoginResp: 登录响应
        """
        pass

    async def pre_login(self, request: LoginReq, client: 'ClientResp', http_request: Request) -> None:
        """
        登录前置处理 - 一比一复刻参考项目LoginHandler接口

        Args:
            request: 登录请求参数
            client: 客户端信息
            http_request: HTTP请求对象
        """
        # 验证码校验 - 复刻参考项目逻辑
        await self._validate_captcha(request)

    async def post_login(self, request: LoginReq, client: 'ClientResp', http_request: Request) -> None:
        """
        登录后置处理 - 一比一复刻参考项目LoginHandler接口

        Args:
            request: 登录请求参数
            client: 客户端信息
            http_request: HTTP请求对象
        """
        # 默认实现为空，子类可以重写
        pass

    @abstractmethod
    def get_auth_type(self) -> AuthTypeEnum:
        """获取认证类型 - 一比一复刻参考项目LoginHandler接口"""
        pass

    @staticmethod
    def check_user_status(user: 'UserEntity'):
        """
        检查用户状态

        复刻参考项目的AbstractLoginHandler.checkUserStatus方法

        Args:
            user: 用户实体
        """

        # 检查用户是否被禁用
        if user.status == DisEnableStatusEnum.DISABLE:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="此账号已被禁用，如有疑问，请联系管理员"
            )

        # TODO: 添加部门状态检查（需要实现DeptService后）
        # CheckUtils.throwIfEqual(DisEnableStatusEnum.DISABLE, dept.getStatus(), "此账号所属部门已被禁用，如有疑问，请联系管理员");

    @staticmethod
    async def authenticate(user: 'UserEntity', client: 'ClientEntity') -> LoginResp:
        """
        执行认证，生成令牌

        完全复刻参考项目的AbstractLoginHandler.authenticate(UserDO user, ClientResp client)方法

        Args:
            user: 用户实体
            client: 客户端实体

        Returns:
            LoginResp: 登录响应
        """

        # 检查用户状态
        AbstractLoginHandler.check_user_status(user)

        # 获取用户ID和租户ID
        user_id = user.id
        tenant_id = 1  # TODO: 从TenantContextHolder获取，目前默认为1

        # 异步获取权限、角色、密码过期天数 (复刻参考项目的CompletableFuture逻辑)
        from apps.system.auth.service.role_permission_service import RolePermissionService

        permissions = await RolePermissionService.list_permission_by_user_id(user_id)
        roles = await RolePermissionService.list_by_user_id(user_id)
        password_expiration_days = 0  # TODO: 从OptionService获取PASSWORD_EXPIRATION_DAYS（0表示永不过期，匹配参考项目默认值）

        # 创建完整的用户上下文 (复刻参考项目的UserContext构造)
        user_context = UserContext(
            permissions=permissions,
            roles=roles,
            password_expiration_days=password_expiration_days
        )

        # 复制用户属性到上下文 (复刻参考项目的BeanUtil.copyProperties(user, userContext))
        # Python方式：使用字段复制而不是deepcopy，避免复制不必要的ORM内部状态
        user_context.id = user.id
        user_context.username = user.username
        user_context.nickname = user.nickname
        user_context.email = user.email
        user_context.phone = user.phone
        user_context.avatar = user.avatar
        user_context.dept_id = user.dept_id
        user_context.pwd_reset_time = user.pwd_reset_time

        # 设置额外属性 (复刻参考项目的client相关设置)
        user_context.tenant_id = tenant_id
        user_context.client_type = client.client_type
        user_context.client_id = client.client_id

        # 设置用户上下文
        UserContextHolder.set_context(user_context)

        # 生成JWT令牌 - 将UserContext序列化到JWT中 (模拟参考项目将UserContext存储到Session)
        # 使用UserContext的模型导出功能，而不是手动构建字典
        token_data = user_context.model_dump(exclude={'roles'}, exclude_none=False)  # 包含None值

        # 确保必需字段不为空
        if not token_data.get('id') or not token_data.get('username'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="用户信息不完整"
            )

        # 处理集合字段
        token_data['permissions'] = list(user_context.permissions) if user_context.permissions else []
        token_data['role_codes'] = list(user_context.role_codes) if user_context.role_codes else []

        # 处理时间字段
        if user_context.pwd_reset_time:
            token_data['pwd_reset_time'] = user_context.pwd_reset_time.isoformat()

        # 确保关键字段存在并有正确的名称
        token_data['user_id'] = token_data['id']  # JWT中间件期望user_id字段

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
            is_super_admin=user_context.is_super_admin,
            is_pwd_expired=user_context.is_password_expired
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
        """验证码校验 - 一比一复刻参考项目AccountLoginHandler.preLogin方法"""
        # 导入验证码缓存（避免循环导入）
        from apps.common.controller.captcha_controller import captcha_cache
        from apps.common.util.validation_utils import ValidationUtils, CaptchaConstants
        from datetime import datetime

        # 只对账号登录进行验证码校验（参考项目中的逻辑）
        from apps.system.auth.model.req.login_req import AccountLoginReq
        if not isinstance(request, AccountLoginReq):
            return

        # 如果没有提供验证码信息，则跳过验证（兼容某些客户端）
        if not hasattr(request, 'uuid') or not request.uuid:
            return

        # 使用ValidationUtils进行验证码校验 - 复刻参考项目逻辑
        ValidationUtils.throw_if_blank(request.captcha, "验证码不能为空")
        ValidationUtils.throw_if_blank(request.uuid, "验证码标识不能为空")

        # 清理过期验证码
        current_time = datetime.now()
        expired_keys = [
            key for key, data in captcha_cache.items()
            if current_time > data['expire_time']
        ]
        for key in expired_keys:
            del captcha_cache[key]

        # 构造验证码缓存键（与验证码生成时的格式保持一致）
        captcha_key = f"captcha:{request.uuid}"

        # 检查验证码UUID是否存在并获取缓存的验证码
        if captcha_key not in captcha_cache:
            ValidationUtils.throw_if_blank("", CaptchaConstants.CAPTCHA_EXPIRED)

        cached_data = captcha_cache[captcha_key]
        captcha_code = cached_data['code']

        # 验证验证码是否存在
        ValidationUtils.throw_if_blank(captcha_code, CaptchaConstants.CAPTCHA_EXPIRED)

        # 验证验证码是否正确（忽略大小写）- 复刻参考项目逻辑
        ValidationUtils.throw_if_not_equal_ignore_case(request.captcha, captcha_code, CaptchaConstants.CAPTCHA_ERROR)

        # 验证成功，删除验证码（一次性使用）
        del captcha_cache[captcha_key]

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
