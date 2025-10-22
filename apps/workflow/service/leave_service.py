# -*- coding: utf-8 -*-

"""
请假流程服务
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.task import TaskState

from apps.common.models.api_response import ApiResponse
from apps.common.models.page_resp import PageResp
from apps.common.config.exception.global_exception_handler import BusinessException
from apps.workflow.model.leave_model import (
    LeaveRequest, LeaveApproval, LeaveStatus, LeaveWorkflowData
)
from apps.workflow.utils.storage import WorkflowFileStorage


class LeaveWorkflowService:
    """请假流程服务类"""

    # 请假类型映射（英文 -> 中文）
    LEAVE_TYPE_MAP = {
        'annual_leave': '年假',
        'sick_leave': '病假',
        'personal_leave': '事假',
        'marriage_leave': '婚假',
        'maternity_leave': '产假',
        'other': '其他'
    }

    def __init__(self):
        self.workflow_dir = Path("apps/workflow/bpmn")
        self.data_dir = Path("apps/workflow/data")
        self.data_dir.mkdir(exist_ok=True)
        
        # 初始化文件存储
        self.storage = WorkflowFileStorage()
        
        # 加载BPMN流程定义
        self.parser = BpmnParser()
        bpmn_file = self.workflow_dir / "leave_request.bpmn"
        if bpmn_file.exists():
            with open(bpmn_file, 'rb') as f:
                self.parser.add_bpmn_str(f.read())
        
        self.spec = self.parser.get_spec("LeaveRequestProcess")
    
    def create_leave_request(self, leave_data: Dict[str, Any]) -> LeaveRequest:
        """创建请假申请"""
        # 生成唯一ID
        leave_id = str(uuid.uuid4())
        process_instance_id = str(uuid.uuid4())  # 生成流程实例ID

        # 计算请假天数
        start_date = datetime.fromisoformat(leave_data["start_date"])
        end_date = datetime.fromisoformat(leave_data["end_date"])
        leave_days = (end_date - start_date).days + 1

        # 创建请假申请
        leave_request = LeaveRequest(
            id=leave_id,
            applicant_name=leave_data["applicant_name"],
            applicant_id=leave_data["applicant_id"],
            leave_type=leave_data["leave_type"],
            start_date=start_date,
            end_date=end_date,
            leave_days=leave_days,
            reason=leave_data["reason"],
            status=LeaveStatus.PENDING,
            process_instance_id=process_instance_id  # 设置流程实例ID
        )

        # 创建工作流实例
        workflow = BpmnWorkflow(self.spec)

        # 设置流程变量（使用 workflow.data 字典）
        workflow.data["leave_request"] = leave_request.dict()
        workflow.data["leave_days"] = leave_days
        workflow.data["applicant_name"] = leave_data["applicant_name"]

        # 启动流程
        workflow.do_engine_steps()

        # 保存流程数据
        workflow_data = LeaveWorkflowData(
            leave_request=leave_request,
            current_task="Task_Manager_Approval",  # 提交后进入直属领导审批
            variables={
                "leave_days": leave_days,
                "applicant_name": leave_data["applicant_name"]
            }
        )
        self._save_workflow_data(process_instance_id, workflow_data)
        self._save_workflow_instance(process_instance_id, workflow)

        return leave_request
    
    def get_leave_request(self, leave_id: str) -> Optional[LeaveRequest]:
        """获取请假申请"""
        # 使用文件存储查询
        instances = self.storage.list_instances()
        
        for instance_data in instances:
            try:
                workflow_data = LeaveWorkflowData.from_dict(instance_data)
                if workflow_data.leave_request.id == leave_id:
                    return workflow_data.leave_request
            except Exception:
                continue
        return None
    
    def get_pending_tasks(self, user_id: str, user_name: str) -> List[Dict[str, Any]]:
        """获取用户的待办任务"""
        pending_tasks = []

        # 使用文件存储查询所有实例
        instances = self.storage.list_instances()

        print(f"[DEBUG get_pending_tasks] 用户 {user_name}({user_id}) 查询待办任务")
        print(f"[DEBUG get_pending_tasks] 共找到 {len(instances)} 个流程实例")

        for instance_data in instances:
            try:
                workflow_data = LeaveWorkflowData.from_dict(instance_data)

                # 检查当前任务是否需要该用户处理
                current_task = workflow_data.current_task
                leave_request = workflow_data.leave_request

                print(f"[DEBUG get_pending_tasks] 实例: {leave_request.id}, 当前任务: {current_task}, 状态: {leave_request.status.value}")

                # 简化逻辑：所有待审批的任务都显示（演示项目）
                if current_task == "Task_Manager_Approval":
                    # 直属领导审批任务
                    leave_request_dict = leave_request.model_dump(by_alias=True, mode='json')
                    self._convert_leave_type_to_chinese(leave_request_dict)
                    task = {
                        "taskId": f"{leave_request.process_instance_id}_manager_approval",
                        "taskName": "直属领导审批",
                        "leaveRequest": leave_request_dict,
                        "processInstanceId": leave_request.process_instance_id,
                        "taskType": "manager_approval"
                    }
                    pending_tasks.append(task)
                    print(f"[DEBUG get_pending_tasks] 添加直属领导审批任务: {task['taskId']}")

                elif current_task == "Task_Dept_Manager_Approval":
                    # 部门经理审批任务
                    leave_request_dict = leave_request.model_dump(by_alias=True, mode='json')
                    self._convert_leave_type_to_chinese(leave_request_dict)
                    task = {
                        "taskId": f"{leave_request.process_instance_id}_dept_manager_approval",
                        "taskName": "部门经理审批",
                        "leaveRequest": leave_request_dict,
                        "processInstanceId": leave_request.process_instance_id,
                        "taskType": "dept_manager_approval"
                    }
                    pending_tasks.append(task)
                    print(f"[DEBUG get_pending_tasks] 添加部门经理审批任务: {task['taskId']}")
                else:
                    print(f"[DEBUG get_pending_tasks] 跳过，当前任务不需要审批: {current_task}")

            except Exception as e:
                print(f"[ERROR get_pending_tasks] 处理实例失败: {e}")
                import traceback
                traceback.print_exc()
                continue

        print(f"[DEBUG get_pending_tasks] 最终返回 {len(pending_tasks)} 个待办任务")
        return pending_tasks
    
    def approve_task(self, process_instance_id: str, task_type: str, approval_data: Dict[str, Any]) -> bool:
        """审批任务"""
        try:
            # 加载工作流数据
            workflow_data = self._load_workflow_data(process_instance_id)
            if not workflow_data:
                raise BusinessException("流程实例不存在")
            
            # 加载工作流实例
            workflow = self._load_workflow_instance(process_instance_id)
            if not workflow:
                raise BusinessException("工作流实例不存在")
            
            # 创建审批记录
            approval = LeaveApproval(
                id=str(uuid.uuid4()),
                leave_request_id=workflow_data.leave_request.id,
                approver_name=approval_data["approver_name"],
                approver_id=approval_data["approver_id"],
                approval_type=task_type,
                action=approval_data.get("action", "approve"),
                comment=approval_data.get("comment"),
                approved=approval_data["approved"]
            )
            
            # 添加审批记录
            workflow_data.approvals.append(approval)
            
            # 根据审批结果推进流程
            if task_type == "manager_approval":
                if approval_data["approved"]:
                    workflow_data.leave_request.status = LeaveStatus.MANAGER_APPROVED
                    # 推进到下一步
                    self._complete_current_task(workflow)
                    
                    # 判断是否需要部门经理审批
                    if workflow_data.leave_request.leave_days >= 3:
                        workflow_data.current_task = "Task_Dept_Manager_Approval"
                    else:
                        workflow_data.leave_request.status = LeaveStatus.APPROVED
                        workflow_data.current_task = None
                else:
                    workflow_data.leave_request.status = LeaveStatus.MANAGER_REJECTED
                    workflow_data.current_task = None
            
            elif task_type == "dept_manager_approval":
                if approval_data["approved"]:
                    workflow_data.leave_request.status = LeaveStatus.DEPT_MANAGER_APPROVED
                    workflow_data.leave_request.status = LeaveStatus.APPROVED
                else:
                    workflow_data.leave_request.status = LeaveStatus.DEPT_MANAGER_REJECTED
                    workflow_data.leave_request.status = LeaveStatus.REJECTED
                
                workflow_data.current_task = None
                # 完成流程
                self._complete_current_task(workflow)
            
            # 保存更新后的数据
            self._save_workflow_data(process_instance_id, workflow_data)
            self._save_workflow_instance(process_instance_id, workflow)
            
            return True
        
        except Exception as e:
            print(f"Error approving task: {e}")
            raise BusinessException(f"审批失败: {str(e)}")
    
    def _complete_current_task(self, workflow: BpmnWorkflow):
        """完成当前任务"""
        # 获取当前任务
        ready_tasks = workflow.get_tasks(state=TaskState.READY)
        for task in ready_tasks:
            task.complete()
        
        # 执行引擎步骤
        workflow.do_engine_steps()
    
    def _is_manager(self, user_id: str, applicant_id: str) -> bool:
        """判断是否为直属领导（简化实现）"""
        # 简化实现：只要不是申请人本人，都可以审批
        # 实际业务中应该查询组织架构关系
        return user_id != applicant_id

    def _is_dept_manager(self, user_id: str) -> bool:
        """判断是否为部门经理（简化实现）"""
        # 简化实现：管理员可以审批所有请假
        # 实际业务中应该查询用户角色和权限
        return True  # 所有用户都可以作为部门经理审批

    @staticmethod
    def _convert_leave_type_to_chinese(leave_request_dict: Dict[str, Any]) -> Dict[str, Any]:
        """将请假类型从英文转换为中文显示"""
        if 'leaveType' in leave_request_dict:
            leave_type = leave_request_dict['leaveType']
            leave_request_dict['leaveTypeText'] = LeaveWorkflowService.LEAVE_TYPE_MAP.get(leave_type, leave_type)
        return leave_request_dict

    def _save_workflow_data(self, process_instance_id: str, data: LeaveWorkflowData):
        """保存工作流数据"""
        self.storage.save_instance(process_instance_id, data.to_dict())
    
    def _load_workflow_data(self, process_instance_id: str) -> Optional[LeaveWorkflowData]:
        """加载工作流数据"""
        data = self.storage.load_instance(process_instance_id)
        if not data:
            return None
        
        try:
            return LeaveWorkflowData.from_dict(data)
        except Exception as e:
            print(f"Error loading workflow data: {e}")
            return None
    
    def _save_workflow_instance(self, process_instance_id: str, workflow: BpmnWorkflow):
        """保存工作流实例"""
        # 这里简化处理，实际应该序列化整个工作流状态
        pass
    
    def _load_workflow_instance(self, process_instance_id: str) -> Optional[BpmnWorkflow]:
        """加载工作流实例"""
        # 这里简化处理，实际应该反序列化工作流状态
        workflow = BpmnWorkflow(self.spec)
        # 重新设置数据（使用 workflow.data 字典）
        workflow_data = self._load_workflow_data(process_instance_id)
        if workflow_data:
            workflow.data["leave_request"] = workflow_data.leave_request.dict()
            workflow.data["leave_days"] = workflow_data.leave_request.leave_days
        return workflow
    
    def get_user_leave_requests(self, user_id: str, status: Optional[str] = None) -> List[LeaveRequest]:
        """获取用户的请假申请列表"""
        leave_requests = []

        # 使用文件存储查询所有实例
        instances = self.storage.list_instances()

        print(f"[DEBUG] 查询用户 {user_id} 的请假申请，共找到 {len(instances)} 个实例")

        for instance_data in instances:
            try:
                workflow_data = LeaveWorkflowData.from_dict(instance_data)
                leave_request = workflow_data.leave_request

                print(f"[DEBUG] 检查实例: leave_id={leave_request.id}, applicant_id={leave_request.applicant_id}, status={leave_request.status.value}")

                # 检查是否为该用户的申请
                if leave_request.applicant_id == user_id:
                    print(f"[DEBUG] 匹配用户 {user_id} 的申请")
                    # 如果指定了状态，则进行过滤
                    if status is None or leave_request.status.value == status:
                        print(f"[DEBUG] 状态匹配或无状态过滤，添加到结果")
                        leave_requests.append(leave_request)
                    else:
                        print(f"[DEBUG] 状态不匹配: 要求={status}, 实际={leave_request.status.value}")
                else:
                    print(f"[DEBUG] 用户ID不匹配: 要求={user_id}, 实际={leave_request.applicant_id}")

            except Exception as e:
                print(f"Error processing instance: {e}")
                import traceback
                traceback.print_exc()
                continue

        # 按创建时间倒序排列
        leave_requests.sort(key=lambda x: x.created_at, reverse=True)
        print(f"[DEBUG] 最终返回 {len(leave_requests)} 条记录")
        return leave_requests

    def get_user_leave_requests_page(
        self,
        user_id: str,
        status: Optional[str] = None,
        page: int = 1,
        size: int = 10
    ) -> PageResp[Dict[str, Any]]:
        """
        获取用户的请假申请分页列表

        Args:
            user_id: 用户ID
            status: 状态过滤
            page: 页码
            size: 每页条数

        Returns:
            PageResp: 分页响应对象
        """
        # 获取所有请假申请
        leave_requests = self.get_user_leave_requests(user_id, status)

        # 分页
        total = len(leave_requests)
        start = (page - 1) * size
        end = start + size
        page_data = leave_requests[start:end]

        # 转换为字典列表（使用camelCase字段名）
        leave_request_dicts = [request.model_dump(by_alias=True, mode='json') for request in page_data]

        # 为每个请假申请添加中文类型显示和时间格式化
        for leave_dict in leave_request_dicts:
            self._convert_leave_type_to_chinese(leave_dict)
            # 添加前端期望的字段名
            if 'createdAt' in leave_dict:
                leave_dict['createTime'] = leave_dict['createdAt']
            if 'updatedAt' in leave_dict:
                leave_dict['updateTime'] = leave_dict['updatedAt']

        # 计算总页数
        pages = (total + size - 1) // size if total > 0 else 0

        # 构造分页响应
        return PageResp(
            list=leave_request_dicts,
            total=total,
            current=page,
            size=size,
            pages=pages
        )
    
    def get_workflow_status(self, process_instance_id: str) -> Dict[str, Any]:
        """获取工作流状态"""
        workflow_data = self._load_workflow_data(process_instance_id)
        if not workflow_data:
            return {"error": "流程实例不存在"}
        
        return {
            "process_instance_id": process_instance_id,
            "leave_request": workflow_data.leave_request.dict(),
            "current_task": workflow_data.current_task,
            "approvals": [approval.dict() for approval in workflow_data.approvals],
            "variables": workflow_data.variables
        }
    
    def get_storage_info(self) -> Dict[str, Any]:
        """获取存储信息"""
        return self.storage.get_storage_info()

    def update_leave_request(self, leave_id: str, update_data: Dict[str, Any]) -> Optional[LeaveRequest]:
        """更新请假申请"""
        # 查找请假申请
        instances = self.storage.list_instances()

        for instance_data in instances:
            try:
                workflow_data = LeaveWorkflowData.from_dict(instance_data)
                leave_request = workflow_data.leave_request

                if leave_request.id == leave_id:
                    # 只允许修改草稿或被拒绝的申请
                    if leave_request.status not in [LeaveStatus.DRAFT, LeaveStatus.REJECTED]:
                        raise BusinessException("只能修改草稿或被拒绝的请假申请")

                    # 更新字段
                    if "leave_type" in update_data:
                        leave_request.leave_type = update_data["leave_type"]
                    if "start_date" in update_data:
                        leave_request.start_date = datetime.fromisoformat(update_data["start_date"])
                    if "end_date" in update_data:
                        leave_request.end_date = datetime.fromisoformat(update_data["end_date"])
                    if "reason" in update_data:
                        leave_request.reason = update_data["reason"]

                    # 重新计算请假天数
                    leave_request.leave_days = (leave_request.end_date - leave_request.start_date).days + 1
                    leave_request.updated_at = datetime.now()

                    # 保存更新
                    self._save_workflow_data(leave_request.process_instance_id, workflow_data)

                    return leave_request

            except Exception as e:
                print(f"Error processing instance: {e}")
                continue

        return None

    def delete_leave_request(self, leave_id: str) -> bool:
        """删除请假申请"""
        # 查找请假申请
        instances = self.storage.list_instances()

        for instance_data in instances:
            try:
                workflow_data = LeaveWorkflowData.from_dict(instance_data)
                leave_request = workflow_data.leave_request

                if leave_request.id == leave_id:
                    # 只允许删除草稿、被拒绝或已取消的申请
                    if leave_request.status not in [LeaveStatus.DRAFT, LeaveStatus.REJECTED, LeaveStatus.CANCELLED]:
                        raise BusinessException("只能删除草稿、被拒绝或已取消的请假申请")

                    # 删除存储的数据
                    process_instance_id = leave_request.process_instance_id
                    if process_instance_id:
                        data_file = self.data_dir / f"{process_instance_id}.json"
                        if data_file.exists():
                            data_file.unlink()

                    return True

            except Exception as e:
                print(f"Error processing instance: {e}")
                continue

        return False