# -*- coding: utf-8 -*-

"""
请假流程控制器
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel, Field, ConfigDict

from apps.common.models.api_response import ApiResponse, create_success_response
from apps.common.models.page_resp import PageResp
from apps.common.config.exception.global_exception_handler import BusinessException
from apps.common.config.logging.logging_config import get_logger
from apps.common.context.user_context import UserContext
from apps.common.dependencies.auth_dependencies import get_current_user
from apps.workflow.service.leave_service import LeaveWorkflowService
from apps.workflow.model.leave_model import LeaveStatus

logger = get_logger(__name__)

router = APIRouter(prefix="/workflow/leave", tags=["请假流程"])


class LeaveRequestCreate(BaseModel):
    """创建请假申请请求"""
    model_config = ConfigDict(
        populate_by_name=True,  # 允许使用字段名或别名
    )

    leave_type: str = Field(..., description="请假类型", alias="leaveType")
    start_date: str = Field(..., description="开始日期 (ISO格式)", alias="startDate")
    end_date: str = Field(..., description="结束日期 (ISO格式)", alias="endDate")
    reason: str = Field(..., description="请假原因")


class LeaveApprovalRequest(BaseModel):
    """审批请求"""
    model_config = ConfigDict(
        populate_by_name=True,
    )

    process_instance_id: str = Field(..., description="流程实例ID", alias="processInstanceId")
    task_type: str = Field(..., description="任务类型", alias="taskType")
    approved: bool = Field(..., description="是否批准")
    comment: Optional[str] = Field(None, description="审批意见")
    action: str = Field("approve", description="审批动作")


class LeaveQuery(BaseModel):
    """请假申请查询"""
    applicant_id: Optional[str] = Field(None, description="申请人ID")
    status: Optional[LeaveStatus] = Field(None, description="状态")
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(10, ge=1, le=100, description="每页条数")


# 创建服务实例
leave_service = LeaveWorkflowService()


@router.post("/request", summary="创建请假申请")
async def create_leave_request(
    request: LeaveRequestCreate,
    current_user: UserContext = Depends(get_current_user)
) -> ApiResponse[Dict[str, Any]]:
    """创建请假申请"""
    try:
        # 从JWT token中提取申请人信息
        applicant_id = str(current_user.id)
        applicant_name = current_user.username

        logger.info(f"创建请假申请: {applicant_name}")

        # 合并申请人信息和请求数据
        request_data = request.dict()
        request_data['applicant_id'] = applicant_id
        request_data['applicant_name'] = applicant_name

        # 创建请假申请
        leave_request = leave_service.create_leave_request(request_data)

        return create_success_response(data=leave_request.model_dump(by_alias=True))

    except Exception as e:
        logger.error(f"创建请假申请失败: {e}")
        raise BusinessException(f"创建请假申请失败: {str(e)}")


@router.get("/request/{leave_id}", summary="获取请假申请详情")
async def get_leave_request(leave_id: str) -> ApiResponse[Dict[str, Any]]:
    """获取请假申请详情"""
    try:
        logger.info(f"获取请假申请详情: {leave_id}")

        leave_request = leave_service.get_leave_request(leave_id)
        if not leave_request:
            raise BusinessException("请假申请不存在")

        return create_success_response(data=leave_request.model_dump(by_alias=True))

    except Exception as e:
        logger.error(f"获取请假申请详情失败: {e}")
        raise BusinessException(f"获取请假申请详情失败: {str(e)}")


@router.put("/request/{leave_id}", summary="更新请假申请")
async def update_leave_request(
    leave_id: str,
    request: LeaveRequestCreate,
    current_user: UserContext = Depends(get_current_user)
) -> ApiResponse[Dict[str, Any]]:
    """更新请假申请"""
    try:
        # 从JWT token中提取申请人信息
        applicant_id = str(current_user.id)
        applicant_name = current_user.username

        logger.info(f"更新请假申请: {leave_id}, 申请人: {applicant_name}")

        # 合并申请人信息和请求数据
        request_data = request.dict()
        request_data['applicant_id'] = applicant_id
        request_data['applicant_name'] = applicant_name

        # 更新请假申请
        leave_request = leave_service.update_leave_request(leave_id, request_data)
        if not leave_request:
            raise BusinessException("请假申请不存在或无法更新")

        return create_success_response(data=leave_request.model_dump(by_alias=True))

    except Exception as e:
        logger.error(f"更新请假申请失败: {e}")
        raise BusinessException(f"更新请假申请失败: {str(e)}")


@router.delete("/request/{leave_id}", summary="删除请假申请")
async def delete_leave_request(leave_id: str) -> ApiResponse[Dict[str, Any]]:
    """删除请假申请"""
    try:
        logger.info(f"删除请假申请: {leave_id}")

        # 删除请假申请
        success = leave_service.delete_leave_request(leave_id)
        if not success:
            raise BusinessException("请假申请不存在或无法删除")

        return create_success_response(data={
            "message": "请假申请删除成功"
        })

    except Exception as e:
        logger.error(f"删除请假申请失败: {e}")
        raise BusinessException(f"删除请假申请失败: {str(e)}")


@router.get("/pending-tasks", summary="获取待办任务")
async def get_pending_tasks(
    current_user: UserContext = Depends(get_current_user)
) -> ApiResponse[Dict[str, Any]]:
    """获取用户的待办任务"""
    try:
        # 从JWT token中提取用户信息
        user_id = str(current_user.id)
        user_name = current_user.username

        logger.info(f"获取待办任务: {user_name} ({user_id})")

        pending_tasks = leave_service.get_pending_tasks(user_id, user_name)

        logger.info(f"待办任务数量: {len(pending_tasks)}")
        if pending_tasks:
            logger.info(f"第一条任务示例: {pending_tasks[0]}")

        return create_success_response(data={
            "pendingTasks": pending_tasks,
            "total": len(pending_tasks)
        })

    except Exception as e:
        logger.error(f"获取待办任务失败: {e}")
        raise BusinessException(f"获取待办任务失败: {str(e)}")


@router.post("/approve", summary="审批任务")
async def approve_task(
    request: LeaveApprovalRequest,
    current_user: UserContext = Depends(get_current_user)
) -> ApiResponse[Dict[str, Any]]:
    """审批任务"""
    try:
        # 从JWT token中提取审批人信息
        approver_id = str(current_user.id)
        approver_name = current_user.username

        logger.info(f"审批任务: {request.process_instance_id}, 审批人: {approver_name}")

        # 合并审批人信息到请求数据
        approval_data = request.dict()
        approval_data['approver_id'] = approver_id
        approval_data['approver_name'] = approver_name

        success = leave_service.approve_task(
            request.process_instance_id,
            request.task_type,
            approval_data
        )

        if success:
            return create_success_response(data={
                "message": "审批成功"
            })
        else:
            raise BusinessException("审批失败")

    except Exception as e:
        logger.error(f"审批任务失败: {e}")
        raise BusinessException(f"审批任务失败: {str(e)}")


@router.get("/my-requests", summary="获取我的请假申请")
async def get_my_requests(
    status: Optional[LeaveStatus] = Query(None, description="状态筛选"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页条数"),
    current_user: UserContext = Depends(get_current_user)
) -> ApiResponse[PageResp[Dict[str, Any]]]:
    """获取我的请假申请列表"""
    try:
        applicant_id = str(current_user.id)
        logger.info(f"获取请假申请列表: 用户ID={applicant_id}, 用户名={current_user.username}, 状态筛选={status}")

        # 使用服务层获取分页结果
        status_str = status.value if status else None
        result = leave_service.get_user_leave_requests_page(applicant_id, status_str, page, size)

        logger.info(f"返回结果: total={result.total}, current_page={result.current}, list_size={len(result.list)}")

        return create_success_response(data=result)

    except Exception as e:
        logger.error(f"获取请假申请列表失败: {e}", exc_info=True)
        raise BusinessException(f"获取请假申请列表失败: {str(e)}")


@router.get("/status", summary="获取流程状态")
async def get_workflow_status() -> ApiResponse[Dict[str, Any]]:
    """获取工作流状态"""
    try:
        # 统计各种状态的数量
        status_counts = {}
        
        import json
        from pathlib import Path
        from apps.workflow.model.leave_model import LeaveWorkflowData
        
        data_dir = Path("apps/workflow/data")
        if data_dir.exists():
            for data_file in data_dir.glob("*.json"):
                try:
                    with open(data_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        workflow_data = LeaveWorkflowData.from_dict(data)
                        status = workflow_data.leave_request.status
                        status_counts[status] = status_counts.get(status, 0) + 1
                
                except Exception:
                    continue
        
        return create_success_response(data={
            "status_counts": status_counts,
            "total": sum(status_counts.values())
        })
    
    except Exception as e:
        logger.error(f"获取流程状态失败: {e}")
        raise BusinessException(f"获取流程状态失败: {str(e)}")