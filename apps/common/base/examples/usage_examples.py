# -*- coding: utf-8 -*-

"""
Excel导出和数据权限使用示例

演示如何使用Excel导出和数据权限功能
"""

from typing import List
from datetime import datetime
from pydantic import BaseModel, Field
from fastapi import HTTPException
from apps.common.base.excel.excel_exporter import excel_property, excel_exporter
from apps.common.base.mapper.data_permission_mapper import (
    DataPermissionMapper, DataPermissionQueryWrapper, PageQuery, create_data_permission_mapper
)
from apps.common.base.model.resp.base_resp import BaseResponse


# 示例响应模型
class UserResponse(BaseResponse):
    """
    用户响应模型示例

    演示如何在响应模型中使用Excel导出配置
    """

    username: str = Field(
        ...,
        description="用户名",
        json_schema_extra={
            "example": "admin",
            **excel_property("用户名", order=2, width=15)
        }
    )

    nickname: str = Field(
        ...,
        description="昵称",
        json_schema_extra={
            "example": "管理员",
            **excel_property("昵称", order=3, width=15)
        }
    )

    email: str = Field(
        ...,
        description="邮箱",
        json_schema_extra={
            "example": "admin@example.com",
            **excel_property("邮箱", order=4, width=25)
        }
    )

    status: int = Field(
        ...,
        description="状态",
        json_schema_extra={
            "example": 1,
            **excel_property("状态", order=5, width=10, converter="ExcelBooleanConverter")
        }
    )

    roles: List[str] = Field(
        default_factory=list,
        description="角色列表",
        json_schema_extra={
            "example": ["管理员", "用户"],
            **excel_property("角色", order=6, width=20, converter="ExcelListConverter")
        }
    )


# 示例实体类
class UserEntity:
    """用户实体示例"""

    def __init__(self, id: int, username: str, nickname: str, email: str, status: int, create_time: datetime):
        self.id = id
        self.username = username
        self.nickname = nickname
        self.email = email
        self.status = status
        self.create_time = create_time


# 使用示例
class ExampleService:
    """示例服务类，演示Excel导出和数据权限的使用"""

    def __init__(self, session):
        self.session = session
        # 创建数据权限映射器
        self.user_mapper = create_data_permission_mapper(session, UserEntity)

    async def export_users_to_excel(self, query_conditions: dict = None) -> bytes:
        """
        导出用户数据到Excel

        Args:
            query_conditions: 查询条件

        Returns:
            Excel文件的字节数据
        """
        try:
            # 1. 构建查询条件
            query_wrapper = DataPermissionQueryWrapper()
            if query_conditions:
                if 'username' in query_conditions:
                    query_wrapper.like('username', query_conditions['username'])
                if 'status' in query_conditions:
                    query_wrapper.eq('status', query_conditions['status'])

            # 2. 查询数据（带数据权限控制）
            users = await self.user_mapper.select_list(query_wrapper)

            # 3. 转换为响应模型
            user_responses = []
            for user in users:
                user_resp = UserResponse(
                    id=user.id,
                    username=user.username,
                    nickname=user.nickname,
                    email=user.email,
                    status=user.status,
                    create_time=user.create_time,
                    create_user_string="系统管理员",
                    disabled=False,
                    roles=["管理员", "用户"]
                )
                user_responses.append(user_resp)

            # 4. 导出Excel
            excel_file = excel_exporter.export(user_responses, UserResponse, "用户列表")
            return excel_file.getvalue()

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"导出Excel失败: {str(e)}")

    async def get_users_with_permission(self, page: int = 1, size: int = 10, filters: dict = None) -> dict:
        """
        带数据权限的分页查询用户

        Args:
            page: 页码
            size: 每页大小
            filters: 过滤条件

        Returns:
            分页查询结果
        """
        try:
            # 1. 构建分页参数
            page_query = PageQuery(page=page, size=size)

            # 2. 构建查询条件
            query_wrapper = DataPermissionQueryWrapper()
            if filters:
                if 'keyword' in filters:
                    # 模糊查询用户名或昵称
                    query_wrapper.like('username', filters['keyword'])
                if 'status' in filters:
                    query_wrapper.eq('status', filters['status'])
                if 'start_date' in filters and 'end_date' in filters:
                    query_wrapper.between('create_time', filters['start_date'], filters['end_date'])

            # 添加排序
            query_wrapper.order_by_desc('create_time')

            # 3. 执行查询（自动应用数据权限）
            result = await self.user_mapper.select_page(page_query, query_wrapper)

            # 4. 转换结果格式
            return {
                'records': [
                    UserResponse(
                        id=user.id,
                        username=user.username,
                        nickname=user.nickname,
                        email=user.email,
                        status=user.status,
                        create_time=user.create_time,
                        create_user_string="系统管理员",
                        disabled=False
                    ) for user in result['records']
                ],
                'total': result['total'],
                'page': result['page'],
                'size': result['size'],
                'pages': result['pages']
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


# 在控制器中的使用示例
class UserController:
    """用户控制器示例"""

    def __init__(self, user_service: ExampleService):
        self.user_service = user_service

    async def export_users(self, username: str = None, status: int = None):
        """
        导出用户Excel

        Args:
            username: 用户名过滤
            status: 状态过滤

        Returns:
            Excel文件流
        """
        query_conditions = {}
        if username:
            query_conditions['username'] = username
        if status is not None:
            query_conditions['status'] = status

        excel_data = await self.user_service.export_users_to_excel(query_conditions)

        # 返回文件响应
        from fastapi.responses import Response
        return Response(
            content=excel_data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=users.xlsx"}
        )

    async def get_users(self, page: int = 1, size: int = 10, keyword: str = None, status: int = None):
        """
        分页查询用户

        Args:
            page: 页码
            size: 每页大小
            keyword: 关键词
            status: 状态

        Returns:
            分页查询结果
        """
        filters = {}
        if keyword:
            filters['keyword'] = keyword
        if status is not None:
            filters['status'] = status

        return await self.user_service.get_users_with_permission(page, size, filters)


# FastAPI路由示例
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/users", tags=["用户管理"])

@router.get("/export")
async def export_users(
    username: str = Query(None, description="用户名过滤"),
    status: int = Query(None, description="状态过滤"),
    session: Session = Depends(get_db_session),
    controller: UserController = Depends(get_user_controller)
):
    \"\"\"导出用户Excel\"\"\"
    return await controller.export_users(username, status)

@router.get("")
async def get_users(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页大小"),
    keyword: str = Query(None, description="搜索关键词"),
    status: int = Query(None, description="状态过滤"),
    controller: UserController = Depends(get_user_controller)
):
    \"\"\"分页查询用户\"\"\"
    return await controller.get_users(page, size, keyword, status)
"""