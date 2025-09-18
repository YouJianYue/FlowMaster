# -*- coding: utf-8 -*-
"""
抽象CRUD控制器和控制器基类

一比一复刻参考项目:
- AbstractCrudController.java
- BaseController.java

@author: FlowMaster
@since: 2025/9/18
"""

from typing import TypeVar, Generic, List, Dict, Any, Optional
from abc import ABC
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from apps.common.models.page_resp import PageResp

# 泛型类型定义 - 一比一对应参考项目
S = TypeVar('S')  # S extends CrudService<L, D, Q, C>
L = TypeVar('L')  # 列表响应类型
D = TypeVar('D')  # 详情响应类型
Q = TypeVar('Q')  # 查询条件类型
C = TypeVar('C')  # 创建/修改请求类型


class PageQuery(BaseModel):
    """分页查询参数 - 对应参考项目 PageQuery"""
    page: int = 1
    size: int = 10


class SortQuery(BaseModel):
    """排序查询参数 - 对应参考项目 SortQuery"""
    sort: Optional[List[str]] = None


class IdsReq(BaseModel):
    """ID列表请求 - 对应参考项目 IdsReq"""
    ids: List[int]


class IdResp(BaseModel):
    """ID响应 - 对应参考项目 IdResp"""
    id: int


class LabelValueResp(BaseModel):
    """标签值响应 - 对应参考项目 LabelValueResp"""
    label: str
    value: str
    disabled: Optional[bool] = None


class AbstractCrudController(Generic[S, L, D, Q, C], ABC):
    """
    抽象CRUD控制器

    一比一复刻参考项目 AbstractCrudController.java
    实现 CrudApiHandler 接口的所有标准CRUD操作
    """

    def __init__(self, base_service: S):
        """
        初始化控制器

        Args:
            base_service: 业务服务实例 - 对应 @Autowired protected S baseService;
        """
        self.base_service = base_service

    # ==================== @CrudApi 标准接口 ====================

    async def page(self, query: Q, page_query: PageQuery) -> PageResp[L]:
        """
        分页查询列表

        一比一复刻参考项目:
        @CrudApi(Api.PAGE)
        @GetMapping
        public BasePageResp<L> page(@Valid Q query, @Valid PageQuery pageQuery)
        """
        return await self.base_service.page(query, page_query)

    async def list(self, query: Q, sort_query: SortQuery) -> List[L]:
        """
        查询列表

        一比一复刻参考项目:
        @CrudApi(Api.LIST)
        @GetMapping({"/list"})
        public List<L> list(@Valid Q query, @Valid SortQuery sortQuery)
        """
        return await self.base_service.list(query, sort_query)

    async def tree(self, query: Q, sort_query: SortQuery) -> List[Dict[str, Any]]:
        """
        查询树列表

        一比一复刻参考项目:
        @CrudApi(Api.TREE)
        @GetMapping({"/tree"})
        public List<Tree<Long>> tree(@Valid Q query, @Valid SortQuery sortQuery)
        """
        return await self.base_service.tree(query, sort_query, False)

    async def get(self, entity_id: int) -> D:
        """
        查询详情

        一比一复刻参考项目:
        @CrudApi(Api.GET)
        @GetMapping({"/{id}"})
        public D get(@PathVariable("id") Long id)
        """
        result = await self.base_service.get(entity_id)
        if result is None:
            raise HTTPException(status_code=404, detail="数据不存在")
        return result

    async def create(self, req: C) -> IdResp:
        """
        创建数据

        一比一复刻参考项目:
        @CrudApi(Api.CREATE)
        @PostMapping
        @Validated({CrudValidationGroup.Create.class})
        public IdResp<Long> create(@RequestBody @Valid C req)
        """
        entity_id = await self.base_service.create(req)
        return IdResp(id=entity_id)

    async def update(self, req: C, entity_id: int) -> None:
        """
        修改数据

        一比一复刻参考项目:
        @CrudApi(Api.UPDATE)
        @PutMapping({"/{id}"})
        @Validated({CrudValidationGroup.Update.class})
        public void update(@RequestBody @Valid C req, @PathVariable("id") Long id)
        """
        await self.base_service.update(req, entity_id)

    async def delete(self, entity_id: int) -> None:
        """
        删除数据

        一比一复刻参考项目:
        @CrudApi(Api.DELETE)
        @DeleteMapping({"/{id}"})
        public void delete(@PathVariable("id") Long id)
        """
        await self.base_service.delete([entity_id])

    async def batch_delete(self, req: IdsReq) -> None:
        """
        批量删除数据

        一比一复刻参考项目:
        @CrudApi(Api.BATCH_DELETE)
        @DeleteMapping
        public void batchDelete(@RequestBody @Valid IdsReq req)
        """
        await self.base_service.delete(req.ids)

    async def export(self, query: Q, sort_query: SortQuery) -> StreamingResponse:
        """
        导出数据

        一比一复刻参考项目:
        @CrudApi(Api.EXPORT)
        @ExcludeFromGracefulResponse
        @GetMapping({"/export"})
        public void export(@Valid Q query, @Valid SortQuery sortQuery, HttpServletResponse response)
        """
        content = await self.base_service.export(query, sort_query)
        return StreamingResponse(
            content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=export.xlsx"}
        )

    async def dict(self, query: Q, sort_query: SortQuery) -> List[LabelValueResp]:
        """
        查询字典列表

        一比一复刻参考项目:
        @CrudApi(Api.DICT)
        @GetMapping({"/dict"})
        public List<LabelValueResp> dict(@Valid Q query, @Valid SortQuery sortQuery)
        """
        return await self.base_service.dict(query, sort_query)

    async def dict_tree(self, query: Q, sort_query: SortQuery) -> List[Dict[str, Any]]:
        """
        查询字典树列表

        一比一复刻参考项目:
        @CrudApi(Api.DICT_TREE)
        @GetMapping({"/dict/tree"})
        public List<Tree<Long>> dictTree(@Valid Q query, @Valid SortQuery sortQuery)
        """
        return await self.base_service.tree(query, sort_query, True)


class BaseController(AbstractCrudController[S, L, D, Q, C]):
    """
    控制器基类

    一比一复刻参考项目 BaseController.java
    继承 AbstractCrudController 并添加权限控制逻辑
    """

    def __init__(self, base_service: S):
        super().__init__(base_service)

    # ==================== 权限处理方法 ====================

    @staticmethod
    def get_api_name(api_type: str) -> str:
        """
        获取 API 名称

        一比一复刻参考项目的 getApiName 方法:
        public static String getApiName(Api api) {
            return switch (api) {
                case PAGE, TREE, LIST -> Api.LIST.name();
                case DELETE, BATCH_DELETE -> Api.DELETE.name();
                default -> api.name();
            };
        }
        """
        if api_type in ['PAGE', 'TREE', 'LIST']:
            return 'LIST'
        elif api_type in ['DELETE', 'BATCH_DELETE']:
            return 'DELETE'
        else:
            return api_type

    async def pre_handle(self, api_type: str, *args, **kwargs) -> bool:
        """
        预处理钩子

        一比一复刻参考项目的 preHandle 方法逻辑:
        - 忽略带 sign 请求权限校验
        - 忽略 @SaIgnore 注解的权限校验
        - 忽略排除路径
        - 不需要校验 DICT、DICT_TREE 接口权限
        - 其他接口需要权限校验
        """
        # 字典接口不需要权限校验（对应参考项目逻辑）
        if api_type in ['DICT', 'DICT_TREE']:
            return True

        # 其他接口的权限校验已在装饰器中处理
        return True


# ==================== API枚举 ====================

class Api:
    """
    API枚举 - 对应参考项目的 Api 枚举
    """
    PAGE = "PAGE"
    LIST = "LIST"
    TREE = "TREE"
    GET = "GET"
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    BATCH_DELETE = "BATCH_DELETE"
    EXPORT = "EXPORT"
    DICT = "DICT"
    DICT_TREE = "DICT_TREE"
