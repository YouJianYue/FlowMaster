# -*- coding: utf-8 -*-
"""
文件服务接口

一比一复刻参考项目 FileService.java
@author: FlowMaster
@since: 2025/10/12
"""

from abc import abstractmethod
from typing import Optional

from apps.common.base.service.base_service import BaseService
from apps.system.core.model.entity.file_entity import FileEntity
from apps.system.core.model.query.file_query import FileQuery
from apps.system.core.model.req.file_req import FileReq
from apps.system.core.model.resp.file_resp import FileResp
from apps.system.core.model.resp.file_upload_resp import FileStatisticsResp
from fastapi import UploadFile


class FileService(BaseService[FileResp, FileResp, FileQuery, FileReq]):
    """
    文件服务接口

    一比一复刻参考项目 FileService
    """

    @abstractmethod
    async def upload(self, file: UploadFile, parent_path: Optional[str] = None) -> dict:
        """
        上传文件

        Args:
            file: 上传的文件
            parent_path: 上级目录

        Returns:
            dict: 文件信息
        """
        pass

    @abstractmethod
    async def create_dir(self, req: FileReq) -> int:
        """
        创建文件夹

        Args:
            req: 创建请求

        Returns:
            int: 文件夹ID
        """
        pass

    @abstractmethod
    async def calc_dir_size(self, dir_id: int) -> int:
        """
        计算文件夹大小

        Args:
            dir_id: 文件夹ID

        Returns:
            int: 文件夹大小（字节）
        """
        pass

    @abstractmethod
    async def statistics(self) -> FileStatisticsResp:
        """
        查询文件资源统计

        Returns:
            FileStatisticsResp: 统计信息
        """
        pass

    @abstractmethod
    async def check(self, file_hash: str) -> Optional[FileResp]:
        """
        检测文件是否存在

        Args:
            file_hash: 文件哈希值

        Returns:
            Optional[FileResp]: 文件信息，不存在则返回None
        """
        pass
