# -*- coding: utf-8 -*-

"""
请假流程数据模型
"""

from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel


class LeaveStatus(str, Enum):
    """请假状态枚举"""
    DRAFT = "draft"  # 草稿
    PENDING = "pending"  # 待审批
    MANAGER_APPROVED = "manager_approved"  # 直属领导已批准
    MANAGER_REJECTED = "manager_rejected"  # 直属领导已拒绝
    DEPT_MANAGER_APPROVED = "dept_manager_approved"  # 部门经理已批准
    DEPT_MANAGER_REJECTED = "dept_manager_rejected"  # 部门经理已拒绝
    APPROVED = "approved"  # 已批准
    REJECTED = "rejected"  # 已拒绝
    CANCELLED = "cancelled"  # 已取消


class LeaveRequest(BaseModel):
    """请假申请模型"""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        json_encoders={datetime: lambda v: v.isoformat()}
    )

    id: str = Field(..., description="请假申请ID")
    applicant_name: str = Field(..., description="申请人姓名")
    applicant_id: str = Field(..., description="申请人ID")
    leave_type: str = Field(..., description="请假类型")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    leave_days: float = Field(..., description="请假天数")
    reason: str = Field(..., description="请假原因")
    status: LeaveStatus = Field(default=LeaveStatus.DRAFT, description="状态")
    process_instance_id: Optional[str] = Field(None, description="流程实例ID")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    create_user_string: Optional[str] = Field(None, description="创建人")
    update_user_string: Optional[str] = Field(None, description="修改人")
    create_time: Optional[str] = Field(None, description="创建时间（字符串）")
    update_time: Optional[str] = Field(None, description="修改时间（字符串）")


class LeaveApproval(BaseModel):
    """请假审批模型"""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        json_encoders={datetime: lambda v: v.isoformat()}
    )

    id: str = Field(..., description="审批ID")
    leave_request_id: str = Field(..., description="请假申请ID")
    approver_name: str = Field(..., description="审批人姓名")
    approver_id: str = Field(..., description="审批人ID")
    approval_type: str = Field(..., description="审批类型")
    action: str = Field(..., description="审批动作")
    comment: Optional[str] = Field(None, description="审批意见")
    approved: bool = Field(..., description="是否批准")
    created_at: datetime = Field(default_factory=datetime.now, description="审批时间")


class LeaveWorkflowData(BaseModel):
    """请假流程数据模型"""
    leave_request: LeaveRequest
    approvals: list[LeaveApproval] = Field(default_factory=list, description="审批记录")
    current_task: Optional[str] = Field(None, description="当前任务")
    variables: Dict[str, Any] = Field(default_factory=dict, description="流程变量")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，支持JSON序列化"""
        return {
            "leave_request": self.leave_request.model_dump(mode='json'),
            "approvals": [approval.model_dump(mode='json') for approval in self.approvals],
            "current_task": self.current_task,
            "variables": self.variables
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LeaveWorkflowData":
        """从字典创建"""
        leave_request = LeaveRequest(**data["leave_request"])
        approvals = [LeaveApproval(**approval) for approval in data.get("approvals", [])]
        return cls(
            leave_request=leave_request,
            approvals=approvals,
            current_task=data.get("current_task"),
            variables=data.get("variables", {})
        )