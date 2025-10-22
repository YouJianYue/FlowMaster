# -*- coding: utf-8 -*-

"""
工作流文件存储工具类
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List


class WorkflowFileStorage:
    """工作流文件存储类"""
    
    def __init__(self, base_path: str = "apps/workflow/data"):
        """初始化存储
        
        Args:
            base_path: 基础存储路径
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录
        self.instances_dir = self.base_path / "instances"
        self.instances_dir.mkdir(exist_ok=True)
        
        self.templates_dir = self.base_path / "templates"
        self.templates_dir.mkdir(exist_ok=True)
    
    def save_instance(self, instance_id: str, data: Dict[str, Any]) -> bool:
        """保存流程实例数据
        
        Args:
            instance_id: 实例ID
            data: 实例数据
            
        Returns:
            bool: 是否保存成功
        """
        try:
            file_path = self.instances_dir / f"{instance_id}.json"
            
            # 添加元数据
            data["_metadata"] = {
                "instance_id": instance_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        
        except Exception as e:
            print(f"保存流程实例失败 {instance_id}: {e}")
            return False
    
    def load_instance(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """加载流程实例数据
        
        Args:
            instance_id: 实例ID
            
        Returns:
            Dict[str, Any]: 实例数据，不存在返回None
        """
        try:
            file_path = self.instances_dir / f"{instance_id}.json"
            
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 更新访问时间
            if "_metadata" in data:
                data["_metadata"]["last_accessed"] = datetime.now().isoformat()
                self.save_instance(instance_id, data)
            
            return data
        
        except Exception as e:
            print(f"加载流程实例失败 {instance_id}: {e}")
            return None
    
    def delete_instance(self, instance_id: str) -> bool:
        """删除流程实例数据
        
        Args:
            instance_id: 实例ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            file_path = self.instances_dir / f"{instance_id}.json"
            
            if file_path.exists():
                file_path.unlink()
                return True
            
            return False
        
        except Exception as e:
            print(f"删除流程实例失败 {instance_id}: {e}")
            return False
    
    def list_instances(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """列出流程实例

        Args:
            filters: 过滤条件

        Returns:
            List[Dict[str, Any]]: 实例列表
        """
        try:
            instances = []

            for file_path in self.instances_dir.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # 应用过滤条件
                    if filters:
                        match = True
                        for key, value in filters.items():
                            if key == "status" and data.get("leave_request", {}).get("status") != value:
                                match = False
                                break
                            elif key == "applicant_id" and data.get("leave_request", {}).get("applicant_id") != value:
                                match = False
                                break

                        if not match:
                            continue

                    instances.append(data)

                except json.JSONDecodeError as e:
                    print(f"JSON解析失败 {file_path}: {e}")
                    # 可选：删除损坏的文件
                    # file_path.unlink()
                    continue
                except Exception as e:
                    print(f"处理文件失败 {file_path}: {e}")
                    continue

            return instances

        except Exception as e:
            print(f"列出流程实例失败: {e}")
            return []
    
    def save_template(self, template_id: str, data: Dict[str, Any]) -> bool:
        """保存流程模板
        
        Args:
            template_id: 模板ID
            data: 模板数据
            
        Returns:
            bool: 是否保存成功
        """
        try:
            file_path = self.templates_dir / f"{template_id}.json"
            
            # 添加元数据
            data["_metadata"] = {
                "template_id": template_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "version": "1.0",
                "type": "template"
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        
        except Exception as e:
            print(f"保存流程模板失败 {template_id}: {e}")
            return False
    
    def load_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """加载流程模板
        
        Args:
            template_id: 模板ID
            
        Returns:
            Dict[str, Any]: 模板数据，不存在返回None
        """
        try:
            file_path = self.templates_dir / f"{template_id}.json"
            
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data
        
        except Exception as e:
            print(f"加载流程模板失败 {template_id}: {e}")
            return None
    
    def get_storage_info(self) -> Dict[str, Any]:
        """获取存储信息
        
        Returns:
            Dict[str, Any]: 存储信息
        """
        try:
            instances_count = len(list(self.instances_dir.glob("*.json")))
            templates_count = len(list(self.templates_dir.glob("*.json")))
            
            # 计算总大小
            total_size = 0
            for file_path in self.base_path.rglob("*.json"):
                total_size += file_path.stat().st_size
            
            return {
                "instances_count": instances_count,
                "templates_count": templates_count,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "base_path": str(self.base_path)
            }
        
        except Exception as e:
            print(f"获取存储信息失败: {e}")
            return {
                "instances_count": 0,
                "templates_count": 0,
                "total_size_bytes": 0,
                "total_size_mb": 0,
                "base_path": str(self.base_path),
                "error": str(e)
            }
    
    def cleanup_old_instances(self, days: int = 30) -> int:
        """清理旧的流程实例
        
        Args:
            days: 保留天数
            
        Returns:
            int: 清理的实例数量
        """
        try:
            import time
            from datetime import timedelta
            
            cutoff_time = datetime.now() - timedelta(days=days)
            cleaned_count = 0
            
            for file_path in self.instances_dir.glob("*.json"):
                try:
                    # 获取文件修改时间
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    
                    # 如果文件太旧，删除它
                    if file_mtime < cutoff_time:
                        file_path.unlink()
                        cleaned_count += 1
                
                except Exception as e:
                    print(f"清理文件失败 {file_path}: {e}")
                    continue
            
            return cleaned_count
        
        except Exception as e:
            print(f"清理旧的流程实例失败: {e}")
            return 0