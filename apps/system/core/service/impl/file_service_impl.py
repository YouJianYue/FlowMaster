# -*- coding: utf-8 -*-
"""
文件服务实现

一比一复刻参考项目 FileServiceImpl.java
@author: FlowMaster
@since: 2025/10/12
"""

import hashlib
import os
from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, func, and_

from apps.system.core.service.file_service import FileService
from apps.system.core.model.entity.file_entity import FileEntity
from apps.system.core.model.query.file_query import FileQuery
from apps.system.core.model.req.file_req import FileReq
from apps.system.core.model.resp.file_resp import FileResp
from apps.system.core.model.resp.file_upload_resp import FileStatisticsResp
from apps.system.core.enums.file_type_enum import FileTypeEnum
from apps.common.config.database.database_session import DatabaseSession
from apps.common.config.logging import get_logger
from apps.common.config.exception.global_exception_handler import BusinessException
from apps.common.context.user_context_holder import UserContextHolder
from apps.common.storage.storage_manager import storage_manager
from apps.common.storage.file_validator import FileValidator
from fastapi import UploadFile

logger = get_logger(__name__)


class FileServiceImpl(FileService):
    """
    文件服务实现

    一比一复刻参考项目 FileServiceImpl
    """

    async def page(self, query: FileQuery, page: int = 1, size: int = 10) -> dict:
        """
        分页查询文件列表

        一比一复刻参考项目 FileServiceImpl.page()
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 导入UserEntity
                from apps.system.core.model.entity.user_entity import UserEntity

                # 构建查询
                stmt = select(FileEntity)

                # 名称模糊查询
                if query.name:
                    stmt = stmt.where(FileEntity.name.like(f'%{query.name}%'))

                # 上级目录查询
                if query.parent_path:
                    stmt = stmt.where(FileEntity.parent_path == query.parent_path)

                # 类型查询
                if query.type is not None:
                    stmt = stmt.where(FileEntity.type == query.type)

                # 存储ID查询
                if query.storage_id:
                    stmt = stmt.where(FileEntity.storage_id == query.storage_id)

                # 按创建时间倒序
                stmt = stmt.order_by(FileEntity.create_time.desc())

                # 计算总数
                count_stmt = select(func.count()).select_from(stmt.subquery())
                total_result = await session.execute(count_stmt)
                total = total_result.scalar()

                # 分页
                stmt = stmt.offset((page - 1) * size).limit(size)
                result = await session.execute(stmt)
                entities = result.scalars().all()

                # 收集所有用户ID
                user_ids = set()
                for entity in entities:
                    if entity.create_user:
                        user_ids.add(entity.create_user)
                    if entity.update_user:
                        user_ids.add(entity.update_user)

                # 批量查询用户信息
                user_map = {}
                if user_ids:
                    user_stmt = select(UserEntity).where(UserEntity.id.in_(list(user_ids)))
                    user_result = await session.execute(user_stmt)
                    users = user_result.scalars().all()
                    user_map = {user.id: user.nickname or user.username for user in users}

                # 转换为响应对象
                file_list = []
                for entity in entities:
                    file_resp = FileResp(
                        id=entity.id,
                        name=entity.name,
                        original_name=entity.original_name,
                        size=entity.size,
                        url=self._build_url(entity),
                        parent_path=entity.parent_path,
                        path=entity.path,
                        extension=entity.extension,
                        content_type=entity.content_type,
                        type=FileTypeEnum(entity.type),
                        sha256=entity.sha256,
                        storage_id=entity.storage_id,
                        create_time=entity.create_time,
                        update_time=entity.update_time,
                        create_user_string=user_map.get(entity.create_user),
                        update_user_string=user_map.get(entity.update_user),
                        disabled=False  # 文件管理不支持禁用功能
                    )
                    file_list.append(file_resp)

                return {
                    "list": file_list,
                    "total": total,
                    "current": page,
                    "size": size,
                    "pages": (total + size - 1) // size
                }

        except Exception as e:
            logger.error(f"分页查询文件列表失败: {e}", exc_info=True)
            raise BusinessException(f"分页查询文件列表失败: {str(e)}")

    async def list(self, query: FileQuery) -> List[FileResp]:
        """列表查询"""
        result = await self.page(query, page=1, size=1000)
        return result['list']

    async def get(self, entity_id: int) -> Optional[FileResp]:
        """根据ID查询详情"""
        try:
            async with DatabaseSession.get_session_context() as session:
                from apps.system.core.model.entity.user_entity import UserEntity

                stmt = select(FileEntity).where(FileEntity.id == entity_id)
                result = await session.execute(stmt)
                entity = result.scalar_one_or_none()

                if not entity:
                    return None

                # 查询创建人和更新人姓名
                create_user_name = None
                update_user_name = None

                if entity.create_user:
                    user_stmt = select(UserEntity).where(UserEntity.id == entity.create_user)
                    user_result = await session.execute(user_stmt)
                    user = user_result.scalar_one_or_none()
                    if user:
                        create_user_name = user.nickname or user.username

                if entity.update_user and entity.update_user != entity.create_user:
                    user_stmt = select(UserEntity).where(UserEntity.id == entity.update_user)
                    user_result = await session.execute(user_stmt)
                    user = user_result.scalar_one_or_none()
                    if user:
                        update_user_name = user.nickname or user.username
                elif entity.update_user == entity.create_user:
                    update_user_name = create_user_name

                return FileResp(
                    id=entity.id,
                    name=entity.name,
                    original_name=entity.original_name,
                    size=entity.size,
                    url=self._build_url(entity),
                    parent_path=entity.parent_path,
                    path=entity.path,
                    extension=entity.extension,
                    content_type=entity.content_type,
                    type=FileTypeEnum(entity.type),
                    sha256=entity.sha256,
                    storage_id=entity.storage_id,
                    create_time=entity.create_time,
                    update_time=entity.update_time,
                    create_user_string=create_user_name,
                    update_user_string=update_user_name,
                    disabled=False
                )

        except Exception as e:
            logger.error(f"查询文件详情失败: {e}", exc_info=True)
            raise BusinessException(f"查询文件详情失败: {str(e)}")

    async def create(self, create_req: FileReq) -> int:
        """
        创建文件（不支持，文件应该通过upload上传）

        一比一复刻参考项目，文件管理没有create接口
        """
        raise BusinessException("文件应该通过upload接口上传")

    async def upload(self, file: UploadFile, parent_path: Optional[str] = None) -> dict:
        """
        上传文件

        一比一复刻参考项目 FileServiceImpl.upload()
        """
        try:
            # 文件验证 - 文件扩展名
            if not FileValidator.validate_file_extension(file.filename):
                raise BusinessException(f"不支持的文件类型: {file.filename}")

            # 读取文件内容
            contents = await file.read()

            # 文件验证 - 文件大小
            if not FileValidator.validate_file_size(len(contents)):
                raise BusinessException(
                    f"文件大小超过限制: {FileValidator.MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
                )

            # 文件验证 - 内容类型一致性
            if not FileValidator.validate_content_type(file.content_type, file.filename):
                raise BusinessException("文件内容类型不匹配")

            # 计算文件哈希
            sha256_hash = hashlib.sha256(contents).hexdigest()

            # 检查文件是否已存在（去重）
            existing_file = await self.check(sha256_hash)
            if existing_file:
                logger.info(f"文件已存在，跳过上传: {existing_file.name}")
                return {
                    "id": existing_file.id,
                    "url": existing_file.url,
                    "th_url": None,
                    "metadata": {
                        "sha256": sha256_hash,
                        "size": existing_file.size,
                        "duplicate": True
                    }
                }

            # 获取文件扩展名
            file_extension = os.path.splitext(file.filename)[1][1:].lower() if file.filename else ""

            # 判断文件类型
            file_type = FileTypeEnum.get_by_extension(file_extension)

            # 生成存储路径
            if parent_path is None:
                parent_path = datetime.now().strftime("/%Y/%m/%d")

            # 生成唯一文件名
            unique_name = FileValidator.generate_unique_filename(file.filename or "unknown")
            file_path = f"{parent_path}/{unique_name}"

            # 重置文件指针
            await file.seek(0)

            # 获取存储处理器并上传文件
            handler = storage_manager.get_default_handler()
            stored_path = await handler.upload_file(file, file_path)

            async with DatabaseSession.get_session_context() as session:
                # 获取当前用户ID和租户ID
                current_user_id = UserContextHolder.get_user_id() or 1
                current_tenant_id = UserContextHolder.get_tenant_id() or 1

                # 创建文件记录
                entity = FileEntity(
                    name=unique_name,
                    original_name=FileValidator.sanitize_filename(file.filename or "unknown"),
                    size=len(contents),
                    parent_path=parent_path,
                    path=stored_path,
                    extension=file_extension,
                    content_type=file.content_type,
                    type=file_type.value,
                    sha256=sha256_hash,
                    storage_id=1,  # 使用默认本地存储
                    tenant_id=current_tenant_id,
                    create_user=current_user_id,
                    update_user=current_user_id
                )

                session.add(entity)
                await session.flush()

                # 构建访问URL
                url = handler.build_url(stored_path)
                entity.url = url

                logger.info(f"文件上传成功: id={entity.id}, name={entity.name}, size={entity.size}, tenant_id={current_tenant_id}")

                return {
                    "id": entity.id,
                    "url": url,
                    "th_url": None,  # TODO: 缩略图支持
                    "metadata": {
                        "sha256": sha256_hash,
                        "size": len(contents),
                        "storage_type": handler.get_type()
                    }
                }

        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"文件上传失败: {e}", exc_info=True)
            raise BusinessException(f"文件上传失败: {str(e)}")

    async def create_dir(self, req: FileReq) -> int:
        """
        创建文件夹

        一比一复刻参考项目 FileServiceImpl.createDir()
        """
        try:
            # 如果没有指定上级目录，默认使用根路径
            if not req.parent_path:
                req.parent_path = "/"

            if not req.original_name:
                raise BusinessException("文件夹名称不能为空")

            async with DatabaseSession.get_session_context() as session:
                # 获取当前用户ID和租户ID
                current_user_id = UserContextHolder.get_user_id() or 1
                current_tenant_id = UserContextHolder.get_tenant_id() or 1

                # 构建文件夹路径
                dir_path = f"{req.parent_path.rstrip('/')}/{req.original_name}"

                # 检查是否已存在
                stmt = select(FileEntity).where(
                    and_(
                        FileEntity.path == dir_path,
                        FileEntity.type == FileTypeEnum.DIR.value
                    )
                )
                result = await session.execute(stmt)
                existing = result.scalar_one_or_none()

                if existing:
                    raise BusinessException(f"文件夹已存在: {dir_path}")

                # 创建文件夹记录
                entity = FileEntity(
                    name=req.original_name,
                    original_name=req.original_name,
                    size=0,
                    parent_path=req.parent_path,
                    path=dir_path,
                    type=FileTypeEnum.DIR.value,
                    storage_id=req.storage_id or 1,
                    tenant_id=current_tenant_id,
                    create_user=current_user_id,
                    update_user=current_user_id
                )

                session.add(entity)
                await session.flush()

                # 在物理文件系统中创建文件夹
                try:
                    handler = storage_manager.get_default_handler()
                    await handler.create_directory(dir_path)
                    logger.info(f"物理文件夹创建成功: {dir_path}")
                except Exception as e:
                    logger.error(f"物理文件夹创建失败: {e}", exc_info=True)
                    # 回滚数据库事务
                    raise BusinessException(f"文件夹创建失败: {str(e)}")

                logger.info(f"创建文件夹成功: id={entity.id}, path={dir_path}, tenant_id={current_tenant_id}")

                return entity.id

        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"创建文件夹失败: {e}", exc_info=True)
            raise BusinessException(f"创建文件夹失败: {str(e)}")

    async def update(self, entity_id: int, update_req: FileReq) -> None:
        """修改文件"""
        try:
            async with DatabaseSession.get_session_context() as session:
                # 查询现有文件
                stmt = select(FileEntity).where(FileEntity.id == entity_id)
                result = await session.execute(stmt)
                entity = result.scalar_one_or_none()

                if not entity:
                    raise BusinessException(f"文件不存在: id={entity_id}")

                # 更新字段
                if update_req.original_name:
                    entity.name = update_req.original_name
                    entity.original_name = update_req.original_name

                entity.update_user = UserContextHolder.get_user_id() or 1
                entity.update_time = datetime.now()

                await session.flush()

                logger.info(f"修改文件成功: id={entity_id}")

        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"修改文件失败: {e}", exc_info=True)
            raise BusinessException(f"修改文件失败: {str(e)}")

    async def delete(self, entity_id: int) -> None:
        """删除文件"""
        await self.batch_delete([entity_id])

    async def batch_delete(self, ids: List[int]) -> None:
        """批量删除文件"""
        try:
            async with DatabaseSession.get_session_context() as session:
                # 查询要删除的文件
                stmt = select(FileEntity).where(FileEntity.id.in_(ids))
                result = await session.execute(stmt)
                entities = result.scalars().all()

                deleted_count = 0

                # 删除实际文件
                for entity in entities:
                    if entity.type != FileTypeEnum.DIR.value:  # 只删除实际文件，不删除目录记录
                        try:
                            handler = storage_manager.get_handler()
                            success = await handler.delete_file(entity.path)
                            if success:
                                deleted_count += 1
                                logger.info(f"删除文件成功: {entity.path}")
                            else:
                                logger.warning(f"文件不存在，跳过删除: {entity.path}")
                        except Exception as e:
                            logger.error(f"删除文件失败: {entity.path}, 错误: {e}")
                            # 继续删除其他文件，不中断整个操作

                    # 删除数据库记录
                    await session.delete(entity)

                await session.flush()

                logger.info(f"批量删除文件完成: 请求删除{len(entities)}个文件，实际删除{deleted_count}个文件")

        except Exception as e:
            logger.error(f"批量删除文件失败: {e}", exc_info=True)
            raise BusinessException(f"批量删除文件失败: {str(e)}")

    async def calc_dir_size(self, dir_id: int) -> int:
        """
        计算文件夹大小

        一比一复刻参考项目 FileServiceImpl.calcDirSize()
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 查询文件夹
                stmt = select(FileEntity).where(FileEntity.id == dir_id)
                result = await session.execute(stmt)
                dir_entity = result.scalar_one_or_none()

                if not dir_entity:
                    raise BusinessException(f"文件夹不存在: id={dir_id}")

                if dir_entity.type != FileTypeEnum.DIR.value:
                    raise BusinessException("不是文件夹")

                # 计算文件夹下所有文件的大小
                stmt = select(func.coalesce(func.sum(FileEntity.size), 0)).where(
                    and_(
                        FileEntity.parent_path.like(f"{dir_entity.path}%"),
                        FileEntity.type != FileTypeEnum.DIR.value
                    )
                )
                result = await session.execute(stmt)
                total_size = result.scalar()

                logger.info(f"计算文件夹大小: dir_id={dir_id}, size={total_size}")

                return total_size

        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"计算文件夹大小失败: {e}", exc_info=True)
            raise BusinessException(f"计算文件夹大小失败: {str(e)}")

    async def statistics(self) -> FileStatisticsResp:
        """
        查询文件资源统计

        一比一复刻参考项目 FileServiceImpl.statistics()
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 统计文件总数和总大小
                stmt = select(
                    func.count(FileEntity.id),
                    func.coalesce(func.sum(FileEntity.size), 0)
                ).where(FileEntity.type != FileTypeEnum.DIR.value)

                result = await session.execute(stmt)
                row = result.one()

                return FileStatisticsResp(
                    total_count=row[0],
                    total_size=row[1]
                )

        except Exception as e:
            logger.error(f"查询文件资源统计失败: {e}", exc_info=True)
            return FileStatisticsResp(total_count=0, total_size=0)

    async def check(self, file_hash: str) -> Optional[FileResp]:
        """
        检测文件是否存在

        一比一复刻参考项目 FileServiceImpl.check()
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                from apps.system.core.model.entity.user_entity import UserEntity

                stmt = select(FileEntity).where(FileEntity.sha256 == file_hash)
                result = await session.execute(stmt)
                entity = result.scalar_one_or_none()

                if not entity:
                    return None

                # 查询创建人和更新人姓名（简化版：check方法不一定需要详细信息）
                create_user_name = None
                update_user_name = None

                if entity.create_user:
                    user_stmt = select(UserEntity).where(UserEntity.id == entity.create_user)
                    user_result = await session.execute(user_stmt)
                    user = user_result.scalar_one_or_none()
                    if user:
                        create_user_name = user.nickname or user.username

                if entity.update_user and entity.update_user != entity.create_user:
                    user_stmt = select(UserEntity).where(UserEntity.id == entity.update_user)
                    user_result = await session.execute(user_stmt)
                    user = user_result.scalar_one_or_none()
                    if user:
                        update_user_name = user.nickname or user.username
                elif entity.update_user == entity.create_user:
                    update_user_name = create_user_name

                return FileResp(
                    id=entity.id,
                    name=entity.name,
                    original_name=entity.original_name,
                    size=entity.size,
                    url=self._build_url(entity),
                    parent_path=entity.parent_path,
                    path=entity.path,
                    extension=entity.extension,
                    content_type=entity.content_type,
                    type=FileTypeEnum(entity.type),
                    sha256=entity.sha256,
                    storage_id=entity.storage_id,
                    create_time=entity.create_time,
                    update_time=entity.update_time,
                    create_user_string=create_user_name,
                    update_user_string=update_user_name,
                    disabled=False
                )

        except Exception as e:
            logger.error(f"检测文件是否存在失败: {e}", exc_info=True)
            return None

    def _build_url(self, entity: FileEntity) -> str:
        """构建文件URL"""
        try:
            handler = storage_manager.get_handler()
            return handler.build_url(entity.path)
        except Exception as e:
            logger.error(f"构建文件URL失败: {e}")
            # 降级处理，返回相对路径
            return f"/files/{entity.path.lstrip('/')}"
