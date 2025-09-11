# -*- coding: utf-8 -*-
"""
用户服务实现

@author: continew-admin
@since: 2025/9/11 11:00
"""

from typing import Optional, Union

from ..user_service import UserService
from apps.system.core.model.resp.user_resp import UserResp
from apps.common.model.page_resp import PageResp


class UserServiceImpl(UserService):
    """用户服务实现"""
    
    async def get_user_page(
        self, 
        dept_id: Optional[Union[int, str]] = None,
        page: int = 1,
        size: int = 10,
        sort: Optional[str] = None
    ) -> PageResp[UserResp]:
        """
        分页查询用户列表
        
        Args:
            dept_id: 部门ID
            page: 页码
            size: 每页大小
            sort: 排序字段
            
        Returns:
            PageResp[UserResp]: 分页用户数据
        """
        # TODO: 实现实际的数据库查询逻辑
        # 目前返回模拟数据，匹配参考项目格式
        
        # 模拟用户数据
        mock_users = [
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
                id="547889293968801824",
                create_user_string="超级管理员",
                create_time="2025-08-14 09:15:22",
                disabled=False,
                update_user_string=None,
                update_time=None,
                username="Alice",
                nickname="Alice",
                gender=2,
                avatar=None,
                email="alice@flowmaster.com",
                phone="13800138001",
                status=1,
                is_system=False,
                description="用户界面设计师",
                dept_id="547887852587843592",
                dept_name="UI部",
                role_ids=["547888897925840929"],
                role_names=["设计师"]
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
                status=1,
                is_system=False,
                description="软件测试工程师",
                dept_id="547887852587843593",
                dept_name="测试部",
                role_ids=["547888897925840930"],
                role_names=["测试员"]
            )
        ]
        
        # 根据部门ID过滤用户（如果提供）
        if dept_id is not None:
            filtered_users = [user for user in mock_users if user.dept_id == str(dept_id)]
        else:
            filtered_users = mock_users
        
        # 简单的分页处理
        total = len(filtered_users)
        start_index = (page - 1) * size
        end_index = start_index + size
        page_users = filtered_users[start_index:end_index]
        
        return PageResp[UserResp](
            list=page_users,
            total=total
        )