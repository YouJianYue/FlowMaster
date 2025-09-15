# -*- coding: utf-8 -*-
"""
用户服务实现

@author: continew-admin
@since: 2025/9/11 11:00
"""

from typing import Optional, Union

from ..user_service import UserService
from apps.system.core.model.resp.user_resp import UserResp
from apps.system.core.model.resp.user_detail_resp import UserDetailResp
from apps.common.models.page_resp import PageResp


class UserServiceImpl(UserService):
    """用户服务实现"""
    
    async def get_user_page(
        self,
        dept_id: Optional[Union[int, str]] = None,
        description: Optional[str] = None,
        status: Optional[int] = None,
        page: int = 1,
        size: int = 10,
        sort: Optional[str] = None
    ) -> PageResp[UserResp]:
        """
        分页查询用户列表

        Args:
            dept_id: 部门ID
            description: 关键词（搜索用户名、昵称等）
            status: 用户状态（1=启用，2=禁用）
            page: 页码
            size: 每页大小
            sort: 排序字段

        Returns:
            PageResp[UserResp]: 分页用户数据
        """
        # TODO: 实现实际的数据库查询逻辑
        # 目前返回模拟数据，匹配参考项目格式
        
        # 模拟用户数据 - 匹配参考项目的实际数据
        mock_users = [
            # 参考项目中的真实用户数据
            UserResp(
                id="547889293968801834",
                create_user_string="超级管理员",
                create_time="2025-08-29 20:07:19",
                disabled=False,
                update_user_string=None,
                update_time=None,
                username="lishuyanla",
                nickname="颜如玉",
                gender=1,
                avatar=None,
                email=None,
                phone=None,
                status=1,
                is_system=False,
                description="书中自有颜如玉，世间多是李莫愁。",
                dept_id=1,
                dept_name="Xxx科技有限公司",
                role_ids=[2, 3, "547888897925840927", "547888897925840928"],
                role_names=["系统管理员", "普通用户", "测试人员", "研发人员"]
            ),
            UserResp(
                id="547889293968801829",
                create_user_string="超级管理员",
                create_time="2025-08-29 20:07:19",
                disabled=False,
                update_user_string=None,
                update_time=None,
                username="Jing",
                nickname="MS-Jing",
                gender=1,
                avatar=None,
                email=None,
                phone=None,
                status=2,  # 禁用状态
                is_system=False,
                description="路虽远，行则将至。",
                dept_id="547887852587843599",
                dept_name="研发一组",
                role_ids=[2, 3, "547888897925840927", "547888897925840928"],
                role_names=["系统管理员", "普通用户", "测试人员", "研发人员"]
            ),
            UserResp(
                id="547889293968801824",
                create_user_string="超级管理员",
                create_time="2025-08-29 20:07:19",
                disabled=False,
                update_user_string=None,
                update_time=None,
                username="Yoofff",
                nickname="Yoofff",
                gender=1,
                avatar=None,
                email=None,
                phone=None,
                status=2,  # 禁用状态
                is_system=False,
                description="弱小和无知不是生存的障碍，傲慢才是。",
                dept_id=1,
                dept_name="Xxx科技有限公司",
                role_ids=[2, "547888897925840928"],
                role_names=["系统管理员", "研发人员"]
            ),
            UserResp(
                id="547889293968801826",
                create_user_string="超级管理员",
                create_time="2025-08-29 20:07:19",
                disabled=False,
                update_user_string=None,
                update_time=None,
                username="AutumnSail",
                nickname="秋登",
                gender=1,
                avatar=None,
                email=None,
                phone=None,
                status=1,  # 启用状态
                is_system=False,
                description="只有追求完美，才能创造奇迹。",
                dept_id="547887852587843602",
                dept_name="研发一组",
                role_ids=[2, "547888897925840928"],
                role_names=["系统管理员", "研发人员"]
            ),
            # 原有的用户数据保留一些
            UserResp(
                id="547889293968801823",
                create_user_string="超级管理员",
                create_time="2025-08-14 08:54:38",
                disabled=False,
                update_user_string=None,
                update_time=None,
                username="Charles",
                nickname="Charles",
                gender=1,
                avatar=None,
                email=None,
                phone=None,
                status=1,
                is_system=False,
                description="代码写到极致，就是艺术。",
                dept_id="547887852587843595",
                dept_name="研发一组",
                role_ids=["547888897925840928"],
                role_names=["研发人员"]
            ),
            UserResp(
                id="547889293968801825",
                create_user_string="超级管理员",
                create_time="2025-08-14 10:30:15",
                disabled=False,
                update_user_string=None,
                update_time=None,
                username="Bob",
                nickname="Bob",
                gender=1,
                avatar=None,
                email="bob@flowmaster.com",
                phone="13900139001",
                status=2,  # 禁用状态
                is_system=False,
                description="软件测试工程师",
                dept_id="547887852587843593",
                dept_name="测试部",
                role_ids=["547888897925840930"],
                role_names=["测试员"]
            )
        ]

        # 应用多条件过滤
        filtered_users = mock_users

        # 按部门ID过滤
        if dept_id is not None:
            filtered_users = [user for user in filtered_users if str(user.dept_id) == str(dept_id)]

        # 按关键词搜索（用户名、昵称、描述）
        if description:
            description_lower = description.lower()
            filtered_users = [user for user in filtered_users
                            if (description_lower in user.username.lower() or
                                description_lower in user.nickname.lower() or
                                (user.description and description_lower in user.description.lower()))]

        # 按状态过滤
        if status is not None:
            filtered_users = [user for user in filtered_users if user.status == status]
        
        # 简单的分页处理
        total = len(filtered_users)
        start_index = (page - 1) * size
        end_index = start_index + size
        page_users = filtered_users[start_index:end_index]
        
        return PageResp[UserResp](
            list=page_users,
            total=total
        )

    async def get_user_detail(self, user_id: Union[int, str]) -> UserDetailResp:
        """
        获取用户详情

        Args:
            user_id: 用户ID

        Returns:
            UserDetailResp: 用户详情数据
        """
        # TODO: 实现实际的数据库查询逻辑
        # 目前返回模拟数据，匹配参考项目格式

        # 模拟根据用户ID返回不同的详情数据
        user_id_str = str(user_id)

        if user_id_str == "547889293968801834":
            return UserDetailResp(
                id="547889293968801834",
                create_user_string="超级管理员",
                create_time="2025-08-29 20:07:19",
                disabled=False,
                update_user_string=None,
                update_time=None,
                username="lishuyanla",
                nickname="颜如玉",
                status=1,
                gender=1,
                dept_id=1,
                dept_name="Xxx科技有限公司",
                role_ids=[2, 3, "547888897925840927", "547888897925840928"],
                role_names=["系统管理员", "普通用户", "测试人员", "研发人员"],
                phone=None,
                email=None,
                is_system=False,
                description="书中自有颜如玉，世间多是李莫愁。",
                avatar=None,
                pwd_reset_time="2025-08-29 09:20:23"
            )
        elif user_id_str == "547889293968801829":
            return UserDetailResp(
                id="547889293968801829",
                create_user_string="超级管理员",
                create_time="2025-08-29 20:07:19",
                disabled=False,
                update_user_string=None,
                update_time=None,
                username="Jing",
                nickname="MS-Jing",
                status=2,
                gender=1,
                dept_id="547887852587843599",
                dept_name="研发一组",
                role_ids=[2, 3, "547888897925840927", "547888897925840928"],
                role_names=["系统管理员", "普通用户", "测试人员", "研发人员"],
                phone=None,
                email=None,
                is_system=False,
                description="路虽远，行则将至。",
                avatar=None,
                pwd_reset_time="2025-08-29 09:20:23"
            )
        elif user_id_str == "547889293968801826":
            return UserDetailResp(
                id="547889293968801826",
                create_user_string="超级管理员",
                create_time="2025-08-29 20:07:19",
                disabled=False,
                update_user_string=None,
                update_time=None,
                username="AutumnSail",
                nickname="秋登",
                status=1,
                gender=1,
                dept_id="547887852587843602",
                dept_name="研发一组",
                role_ids=[2, "547888897925840928"],
                role_names=["系统管理员", "研发人员"],
                phone=None,
                email=None,
                is_system=False,
                description="只有追求完美，才能创造奇迹。",
                avatar=None,
                pwd_reset_time="2025-08-29 09:20:23"
            )
        elif user_id_str == "547889293968801823":
            return UserDetailResp(
                id="547889293968801823",
                create_user_string="超级管理员",
                create_time="2025-08-14 08:54:38",
                disabled=False,
                update_user_string=None,
                update_time=None,
                username="Charles",
                nickname="Charles",
                status=1,
                gender=1,
                dept_id="547887852587843595",
                dept_name="研发一组",
                role_ids=["547888897925840928"],
                role_names=["研发人员"],
                phone=None,
                email=None,
                is_system=False,
                description="代码写到极致，就是艺术。",
                avatar=None,
                pwd_reset_time="2025-08-14 08:20:00"
            )
        else:
            # 默认用户数据
            return UserDetailResp(
                id=user_id_str,
                create_user_string="系统管理员",
                create_time="2025-09-14 10:00:00",
                disabled=False,
                update_user_string=None,
                update_time=None,
                username="user" + user_id_str[-4:],
                nickname="用户" + user_id_str[-4:],
                status=1,
                gender=0,
                dept_id=1,
                dept_name="默认部门",
                role_ids=[3],
                role_names=["普通用户"],
                phone=None,
                email=None,
                is_system=False,
                description="默认用户",
                avatar=None,
                pwd_reset_time="2025-09-14 10:00:00"
            )