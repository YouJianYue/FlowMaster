# -*- coding: utf-8 -*-

"""
控制器基类

根据实际项目需要，自行重写 CRUD 接口或增加自定义通用业务接口

@param S: 业务接口
@param L: 列表类型
@param D: 详情类型
@param Q: 查询条件类型
@param C: 创建或修改请求参数类型

"""

from typing import Generic, TypeVar, List
from fastapi import HTTPException, Query
from apps.common.base.service.base_service import BaseService, L, D, Q, C

# 业务服务类型
S = TypeVar('S', bound=BaseService)


class BaseController(Generic[S, L, D, Q, C]):
    """控制器基类"""

    def __init__(self, service: S):
        self.service = service

    async def page(
            self,
            query: Q,
            page: int = Query(1, ge=1, description="页码"),
            size: int = Query(10, ge=1, le=100, description="每页数量")
    ) -> dict:
        """分页查询"""
        try:
            return await self.service.page(query, page, size)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def list(self, query: Q) -> List[L]:
        """列表查询"""
        try:
            return await self.service.list(query)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get(self, entity_id: int) -> D:
        """根据ID查询详情"""
        try:
            result = await self.service.get(entity_id)
            if result is None:
                raise HTTPException(status_code=404, detail=f"ID为 {entity_id} 的记录不存在")
            return result
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def create(self, create_req: C) -> dict:
        """创建"""
        try:
            entity_id = await self.service.create(create_req)
            return {"id": entity_id, "message": "创建成功"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def update(self, entity_id: int, update_req: C) -> dict:
        """修改"""
        try:
            await self.service.update(entity_id, update_req)
            return {"message": "修改成功"}
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def delete(self, entity_id: int) -> dict:
        """删除"""
        try:
            await self.service.delete(entity_id)
            return {"message": "删除成功"}
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def batch_delete(self, ids: List[int]) -> dict:
        """批量删除"""
        try:
            if not ids:
                raise HTTPException(status_code=400, detail="请选择要删除的记录")
            await self.service.batch_delete(ids)
            return {"message": f"成功删除 {len(ids)} 条记录"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


class CrudApi:
    """CRUD API 枚举类"""

    PAGE = "page"
    LIST = "list"
    GET = "get"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    BATCH_DELETE = "batch_delete"
    DICT = "dict"
    DICT_TREE = "dict_tree"


def get_api_name(api: str) -> str:
    """获取 API 名称"""
    api_mapping = {
        CrudApi.PAGE: "list",
        CrudApi.LIST: "list",
        CrudApi.DELETE: "delete",
        CrudApi.BATCH_DELETE: "delete"
    }
    return api_mapping.get(api, api)
