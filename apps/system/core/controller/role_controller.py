# -*- coding: utf-8 -*-
"""
角色管理控制器

一比一复刻参考项目 RoleController.java
严格按照 @CrudRequestMapping 和继承 BaseController 的架构

@author: FlowMaster
@since: 2025/9/18
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Path, Body, Depends, HTTPException
from apps.common.base.controller.base_controller import BaseController, PageQuery, SortQuery, IdsReq
from apps.common.decorators import require_permission
from apps.common.models.api_response import ApiResponse, create_success_response
from apps.common.models.page_resp import PageResp
from apps.common.enums.data_scope_enum import DataScopeEnum
from apps.system.core.service.role_service import get_role_service
from apps.system.core.service.menu_service import get_menu_service, MenuService
from apps.system.core.service.user_role_service import get_user_role_service
from apps.system.core.model.resp.role_resp import RoleResp, RoleDetailResp, RolePermissionResp, RoleUserResp
from apps.system.core.model.req.role_req import RoleReq
from apps.system.core.model.req.role_permission_update_req import RolePermissionUpdateReq
from apps.system.core.model.query.role_query import RoleQuery, RoleUserQuery

# 创建路由器
router = APIRouter(prefix="/system/role", tags=["角色管理 API"])


class RoleController(BaseController):
    """
    角色管理 API

    一比一复刻参考项目 RoleController.java:

    @CrudRequestMapping(value = "/system/role", api = {Api.LIST, Api.GET, Api.CREATE, Api.UPDATE, Api.BATCH_DELETE, Api.DICT})
    public class RoleController extends BaseController<RoleService, RoleResp, RoleDetailResp, RoleQuery, RoleReq>
    """

    def __init__(self):
        # 注入依赖服务 - 对应参考项目的依赖注入
        self.role_service = get_role_service()
        self.user_role_service = get_user_role_service()  # 对应 private final UserRoleService userRoleService;
        self.menu_service = get_menu_service()  # 对应 private final MenuService menuService;

        # 使用统一的日志配置
        from apps.common.config.logging.logging_config import get_logger
        self.logger = get_logger(f"system.{self.__class__.__name__}")

        # 调用父类构造函数 - 对应继承 BaseController
        super().__init__(self.role_service)

    # ==================== BaseController方法适配 ====================

    async def page(self, query, page_query):
        """适配分页查询到角色服务"""
        # 构建过滤条件
        filters = {}
        if hasattr(query, 'name') and query.name:
            filters['name'] = query.name
        if hasattr(query, 'code') and query.code:
            filters['code'] = query.code
        if hasattr(query, 'description') and query.description:
            filters['description'] = query.description

        return await self.role_service.list_roles_with_pagination(
            page=page_query.page,
            size=page_query.size,
            **filters
        )

    async def list(self, query, sort_query):
        """适配列表查询到角色服务"""
        # 构建过滤条件
        filters = {}
        if hasattr(query, 'name') and query.name:
            filters['name'] = query.name
        if hasattr(query, 'code') and query.code:
            filters['code'] = query.code
        if hasattr(query, 'description') and query.description:
            filters['description'] = query.description

        # 添加排序条件
        if hasattr(sort_query, 'sort') and sort_query.sort:
            filters['sort'] = sort_query.sort

        return await self.role_service.list_simple_roles(**filters)

    async def get(self, entity_id: int):
        """适配详情查询到角色服务"""
        from apps.system.core.model.resp.role_resp import RoleDetailResp

        role = await self.role_service.get_role_by_id(entity_id)
        if not role:
            return None

        # 查询角色关联的菜单ID - 针对超级管理员特殊处理
        try:
            if role.code == "super_admin":
                # 超级管理员返回所有启用菜单的ID
                menu_ids = await self.role_service.get_all_menu_ids()
                self.logger.info(f"超级管理员角色{entity_id}拥有所有菜单权限: {len(menu_ids)}个菜单")
            else:
                # 普通角色从角色菜单关联表查询
                menu_ids = await self.role_service.get_role_menu_ids(entity_id)
                self.logger.info(f"角色{entity_id}关联的菜单ID: {menu_ids}")
        except Exception as e:
            self.logger.error(f"查询角色菜单关联失败: {e}", exc_info=True)
            menu_ids = []  # 失败时返回空列表

        # 转换为详情响应模型 - 一比一复刻参考项目格式
        role_detail = RoleDetailResp(
            id=role.id,  # 保持原始数字类型，不转换为字符串
            name=role.name,
            code=role.code,
            description=role.description,
            data_scope=DataScopeEnum.from_value_code(role.data_scope).value_code,  # 使用.value_code返回数字
            sort=role.sort,
            is_system=role.is_system,
            menu_check_strictly=True,  # 参考项目默认为true
            dept_check_strictly=True,  # 参考项目默认为true
            menu_ids=menu_ids,
            dept_ids=None,  # 参考项目返回null而不是空数组
            disabled=role.is_system,  # 系统内置角色不可操作
            create_user_string="超级管理员",
            create_time=role.create_time.strftime("%Y-%m-%d %H:%M:%S") if role.create_time else None,
            update_user_string=None,
            update_time=role.update_time.strftime("%Y-%m-%d %H:%M:%S") if role.update_time else None
        )

        return role_detail

    async def create(self, req):
        """适配创建到角色服务"""
        from apps.common.base.controller.base_controller import IdResp

        success = await self.role_service.create_role(
            name=req.name,
            code=req.code,
            description=req.description or "",
            data_scope=req.data_scope.value if hasattr(req.data_scope, 'value') else str(req.data_scope),
            sort=req.sort or 0
        )

        if not success:
            raise HTTPException(status_code=400, detail="创建角色失败")

        # 查询刚创建的角色以获取ID
        role = await self.role_service.get_role_by_code(req.code)
        if not role:
            raise HTTPException(status_code=500, detail="创建成功但无法获取角色信息")

        return IdResp(id=role.id)

    async def update(self, req, entity_id: int):
        """适配更新到角色服务"""
        success = await self.role_service.update_role(
            role_id=entity_id,
            name=req.name,
            code=req.code,
            description=req.description,
            data_scope=req.data_scope.value if hasattr(req.data_scope, 'value') else str(req.data_scope),
            sort=req.sort
        )

        if not success:
            raise HTTPException(status_code=400, detail="更新角色失败")

    async def batch_delete(self, req):
        """适配批量删除到角色服务"""
        success = await self.role_service.delete_roles(req.ids)

        if not success:
            raise HTTPException(status_code=400, detail="删除角色失败")

    async def dict(self, query, sort_query):
        """适配字典查询到角色服务"""
        # 构建过滤条件
        filters = {}
        if hasattr(query, 'name') and query.name:
            filters['name'] = query.name
        if hasattr(query, 'code') and query.code:
            filters['code'] = query.code
        if hasattr(query, 'description') and query.description:
            filters['description'] = query.description

        # 添加排序条件
        if hasattr(sort_query, 'sort') and sort_query.sort:
            filters['sort'] = sort_query.sort

        return await self.role_service.list_roles_for_dict(**filters)


# 创建控制器实例
role_controller = RoleController()


# ==================== @CrudRequestMapping 标准接口 ====================

@router.get("", response_model=ApiResponse[PageResp[RoleResp]], summary="分页查询角色列表")
@require_permission("system:role:list")
async def page(
        query: RoleQuery = Depends(),
        page_query: PageQuery = Depends()
):
    """
    分页查询角色列表

    对应参考项目的 @CrudApi(Api.PAGE) 接口
    继承自 BaseController 的标准 page 方法
    """
    result = await role_controller.page(query, page_query)
    return create_success_response(data=result)


@router.get("/list", response_model=ApiResponse[List[RoleResp]], summary="查询角色列表")
@require_permission("system:role:list")
async def list_roles(
        query: RoleQuery = Depends(),
        sort_query: SortQuery = Depends()
):
    """
    查询角色列表

    对应参考项目的 @CrudApi(Api.LIST) 接口
    继承自 BaseController 的标准 list 方法
    """
    result = await role_controller.list(query, sort_query)
    return create_success_response(data=result)


@router.get("/{role_id}", response_model=ApiResponse[RoleDetailResp], summary="查询角色详情")
@require_permission("system:role:list")
async def get_role(role_id: int = Path(..., description="ID", example=1)):
    """
    查询角色详情

    对应参考项目的 @CrudApi(Api.GET) 接口
    继承自 BaseController 的标准 get 方法
    """
    result = await role_controller.get(role_id)
    if result is None:
        raise HTTPException(status_code=404, detail="角色不存在")
    return create_success_response(data=result)


@router.post("", response_model=ApiResponse[Dict[str, int]], summary="创建角色")
@require_permission("system:role:create")
async def create_role(req: RoleReq = Body(...)):
    """
    创建角色

    对应参考项目的 @CrudApi(Api.CREATE) 接口
    继承自 BaseController 的标准 create 方法
    """
    result = await role_controller.create(req)
    # 修复 .dict() 过时警告，使用 .model_dump()
    return create_success_response(data=result.model_dump())


@router.put("/{role_id}", response_model=ApiResponse[None], summary="修改角色")
@require_permission("system:role:update")
async def update_role(
        role_id: int = Path(..., description="ID", example=1),
        req: RoleReq = Body(...)
):
    """
    修改角色

    对应参考项目的 @CrudApi(Api.UPDATE) 接口
    继承自 BaseController 的标准 update 方法
    """
    await role_controller.update(req, role_id)
    return create_success_response(data=None)


@router.delete("", response_model=ApiResponse[None], summary="批量删除角色")
@require_permission("system:role:delete")
async def batch_delete_roles(req: IdsReq = Body(...)):
    """
    批量删除角色

    对应参考项目的 @CrudApi(Api.BATCH_DELETE) 接口
    继承自 BaseController 的标准 batch_delete 方法
    """
    await role_controller.batch_delete(req)
    return create_success_response(data=None)


@router.get("/dict", response_model=ApiResponse[List[Dict[str, Any]]], summary="查询角色字典列表")
async def get_role_dict(
        query: RoleQuery = Depends(),
        sort_query: SortQuery = Depends()
):
    """
    查询角色字典列表

    对应参考项目的 @CrudApi(Api.DICT) 接口
    继承自 BaseController 的标准 dict 方法
    无需权限验证（对应参考项目设计）
    """
    result = await role_controller.dict(query, sort_query)
    return create_success_response(data=result)


# ==================== 角色特有接口 ====================

@router.get("/permission/tree", response_model=ApiResponse[List[RolePermissionResp]], summary="查询角色权限树列表")
@require_permission("system:role:updatePermission")
async def list_permission_tree(
    menu_service: MenuService = Depends(get_menu_service)
):
    """
    查询角色权限树列表

    一比一复刻参考项目:
    @Operation(summary = "查询角色权限树列表", description = "查询角色权限树列表")
    @SaCheckPermission("system:role:updatePermission")
    @GetMapping("/permission/tree")
    public List<RolePermissionResp> listPermissionTree()
    """
    # 对应参考项目逻辑:
    # List<Tree<Long>> treeList = menuService.tree(null, null, false);
    # return BeanUtil.copyToList(treeList, RolePermissionResp.class);

    # 获取权限树数据
    tree_list = await menu_service.get_permission_tree()
    
    # 使用 Pydantic 模型转换
    def convert_to_permission_resp(nodes: List[Dict[str, Any]]) -> List[RolePermissionResp]:
        """递归转换权限树节点为 RolePermissionResp 模型"""
        result = []
        for node in nodes:
            # 递归处理子节点
            children = convert_to_permission_resp(node.get("children", [])) if node.get("children") else []
            
            # 创建 RolePermissionResp 实例
            permission_node = RolePermissionResp(
                id=str(node.get("id", "")),
                title=node.get("title", ""),
                parent_id=str(node.get("parentId", "0")),
                type=node.get("type", 1),
                permission=node.get("permission", ""),
                children=children,
                permissions=[]  # 权限列表，用于按钮权限勾选
            )
            result.append(permission_node)
        return result

    # 转换数据格式
    formatted_tree = convert_to_permission_resp(tree_list)
    return create_success_response(data=formatted_tree)


@router.put("/{role_id}/permission", summary="修改权限")
@require_permission("system:role:updatePermission")
async def update_permission(
        role_id: int = Path(..., description="ID", example=1),
        req: RolePermissionUpdateReq = Body(...)
):
    """
    修改权限

    一比一复刻参考项目:
    @Operation(summary = "修改权限", description = "修改角色的功能权限")
    @SaCheckPermission("system:role:updatePermission")
    @PutMapping("/{id}/permission")
    public void updatePermission(@PathVariable("id") Long id, @RequestBody @Valid RolePermissionUpdateReq req)
    """
    success = await role_controller.role_service.update_permission(
        role_id,
        req.menu_ids,
        req.menu_check_strictly
    )
    if not success:
        raise HTTPException(status_code=400, detail="修改权限失败")


# ==================== 用户角色管理接口 ====================

@router.get("/{role_id}/user", response_model=PageResp[RoleUserResp], summary="分页查询关联用户")
@require_permission("system:role:list")
async def page_user(
        role_id: int = Path(..., description="ID", example=1),
        query: RoleUserQuery = Depends(),
        page_query: PageQuery = Depends()
):
    """
    分页查询关联用户

    一比一复刻参考项目:
    @Operation(summary = "分页查询关联用户", description = "分页查询角色关联的用户列表")
    @SaCheckPermission("system:role:list")
    @GetMapping("/{id}/user")
    public BasePageResp<RoleUserResp> pageUser(@PathVariable("id") Long id, @Valid RoleUserQuery query, @Valid PageQuery pageQuery)
    """
    # 设置角色ID到查询条件
    query.role_id = role_id
    result = await role_controller.user_role_service.page_user(query, page_query)
    return result


@router.post("/{role_id}/user", summary="分配用户")
@require_permission("system:role:assign")
async def assign_to_users(
        role_id: int = Path(..., description="ID", example=1),
        user_ids: List[int] = Body(..., description="用户ID列表", example=[1, 2, 3])
):
    """
    分配用户到角色

    一比一复刻参考项目:
    @Operation(summary = "分配用户", description = "将用户分配给角色")
    @SaCheckPermission("system:role:assign")
    @PostMapping("/{id}/user")
    public void assignToUsers(@PathVariable("id") Long id, @RequestBody @Valid List<Long> userIds)
    """
    if not user_ids:
        raise HTTPException(status_code=400, detail="用户ID列表不能为空")

    success = await role_controller.role_service.assign_to_users(role_id, user_ids)
    if not success:
        raise HTTPException(status_code=400, detail="分配用户失败")


@router.delete("/user", summary="取消分配用户")
@require_permission("system:role:unassign")
async def unassign_from_users(
        user_role_ids: List[int] = Body(..., description="用户角色关联ID列表", example=[1, 2, 3])):
    """
    取消分配用户

    一比一复刻参考项目:
    @Operation(summary = "取消分配用户", description = "取消用户与角色的分配关系")
    @SaCheckPermission("system:role:unassign")
    @DeleteMapping("/user")
    public void unassignFromUsers(@RequestBody @Valid List<Long> userRoleIds)
    """
    if not user_role_ids:
        raise HTTPException(status_code=400, detail="用户角色关联ID列表不能为空")

    success = await role_controller.user_role_service.delete_by_ids(user_role_ids)
    if not success:
        raise HTTPException(status_code=400, detail="取消分配用户失败")


@router.get("/{role_id}/user/id", response_model=List[int], summary="查询关联用户ID")
@require_permission("system:role:list")
async def list_user_id(role_id: int = Path(..., description="ID", example=1)):
    """
    查询关联用户ID

    一比一复刻参考项目:
    @Operation(summary = "查询关联用户ID", description = "查询角色关联的所有用户ID")
    @SaCheckPermission("system:role:list")
    @GetMapping("/{id}/user/id")
    public List<Long> listUserId(@PathVariable("id") Long id)
    """
    result = await role_controller.user_role_service.list_user_id_by_role_id(role_id)
    return result
