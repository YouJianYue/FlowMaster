# -*- coding: utf-8 -*-

"""
字典项服务 - 一比一复刻参考项目的DictItemServiceImpl
"""

import inspect
import pkgutil
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from apps.system.core.model.entity.dict_item_entity import DictItemEntity
from apps.system.core.model.entity.dict_entity import DictEntity
from apps.common.config.database.database_session import DatabaseSession
from apps.common.config.logging import get_logger
from apps.common.context.user_context_holder import UserContextHolder

logger = get_logger(__name__)


class DictItemService:
    """
    字典项业务服务

    一比一复刻参考项目: DictItemServiceImpl
    """

    # 枚举字典缓存（一比一复刻 ENUM_DICT_CACHE）
    _ENUM_DICT_CACHE: Dict[str, List[Dict[str, Any]]] = {}
    _initialized = False

    def __init__(self):
        """初始化时加载枚举字典"""
        if not DictItemService._initialized:
            self._init_enum_dict_cache()
            DictItemService._initialized = True

    async def list_by_dict_code(self, dict_code: str) -> List[Dict[str, Any]]:
        """
        根据字典编码查询字典项列表
        一比一复刻参考项目 DictItemServiceImpl.listByDictCode()

        实现逻辑（完全一致）:
        return Optional.ofNullable(ENUM_DICT_CACHE.get(dictCode.toLowerCase()))
            .orElseGet(() -> baseMapper.listByDictCode(dictCode));

        Args:
            dict_code: 字典编码

        Returns:
            List[Dict[str, Any]]: 字典项列表，格式为 LabelValueResp
        """
        # 🔥 一比一复刻：先查枚举缓存，再查数据库
        dict_code_lower = dict_code.lower()

        # 优先返回枚举缓存
        if dict_code_lower in self._ENUM_DICT_CACHE:
            logger.debug(f"从枚举缓存返回字典: {dict_code}")
            return self._ENUM_DICT_CACHE[dict_code_lower]

        # 枚举缓存中没有，查询数据库
        return await self._list_from_database(dict_code)

    async def _list_from_database(self, dict_code: str) -> List[Dict[str, Any]]:
        """
        从数据库查询字典项（一比一复刻 baseMapper.listByDictCode()）

        Args:
            dict_code: 字典编码

        Returns:
            List[Dict[str, Any]]: 字典项列表
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 先根据字典编码查询字典ID
                dict_stmt = select(DictEntity.id).where(DictEntity.code == dict_code)
                dict_result = await session.execute(dict_stmt)
                dict_id = dict_result.scalar_one_or_none()

                if dict_id is None:
                    logger.warning(f"字典编码不存在: {dict_code}")
                    return []

                # 查询字典项（只查询启用状态的）
                stmt = (
                    select(DictItemEntity)
                    .where(DictItemEntity.dict_id == dict_id)
                    .where(DictItemEntity.status == 1)  # 启用状态
                    .order_by(DictItemEntity.sort.asc())
                )
                result = await session.execute(stmt)
                dict_items = result.scalars().all()

                # 转换为 LabelValueResp 格式
                return [
                    {
                        "label": item.label,
                        "value": item.value
                    }
                    for item in dict_items
                ]

        except Exception as e:
            logger.error(f"查询字典项失败 [{dict_code}]: {e}", exc_info=True)
            return []

    def _init_enum_dict_cache(self):
        """
        初始化枚举字典缓存（一比一复刻 @PostConstruct init()）

        一比一复刻参考项目逻辑:
        1. 扫描所有实现BaseEnum的枚举类
        2. 转换为LabelValueResp格式
        3. 缓存到ENUM_DICT_CACHE（key为类名转下划线小写）
        """
        try:
            import apps.common.enums as common_enums
            import apps.system.core.enums as system_enums

            enum_packages = [common_enums, system_enums]

            for package in enum_packages:
                self._scan_and_cache_enums(package)

            logger.debug(f"枚举字典已缓存到内存: {list(self._ENUM_DICT_CACHE.keys())}")

        except Exception as e:
            logger.error(f"初始化枚举字典缓存失败: {e}", exc_info=True)

    def _scan_and_cache_enums(self, package):
        """
        扫描并缓存枚举（一比一复刻 ClassUtil.scanPackageBySuper()）

        Args:
            package: 要扫描的包
        """
        try:
            # 获取包路径
            package_path = package.__path__
            package_name = package.__name__

            # 遍历包中的所有模块
            for _, module_name, _ in pkgutil.iter_modules(package_path):
                try:
                    full_module_name = f"{package_name}.{module_name}"
                    module = __import__(full_module_name, fromlist=[module_name])

                    # 检查模块中的所有类
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        # 检查是否是枚举类，且有必要的属性
                        logger.debug(f"检查类: {name} in {module_name}")
                        if self._is_base_enum(obj):
                            enum_dict = self._to_enum_dict(obj)
                            if enum_dict:
                                # 类名转下划线小写（DataScopeEnum -> data_scope_enum）
                                key = self._to_underline_case(name).lower()
                                self._ENUM_DICT_CACHE[key] = enum_dict
                                logger.debug(f"缓存枚举字典: {key} ({name})")
                        else:
                            logger.debug(f"跳过类 {name}: 不是BaseEnum")

                except Exception as e:
                    logger.debug(f"扫描模块失败 {module_name}: {e}")
                    continue

        except Exception as e:
            logger.error(f"扫描包失败: {e}", exc_info=True)

    def _is_base_enum(self, cls) -> bool:
        """
        检查是否是BaseEnum（一比一复刻）

        Args:
            cls: 类对象

        Returns:
            bool: 是否是BaseEnum
        """
        try:
            # 检查是否是枚举类
            from enum import Enum
            if not issubclass(cls, Enum):
                logger.debug(f"类 {cls.__name__} 不是Enum子类")
                return False

            # 检查是否有必要的属性（value_code, description）
            if not hasattr(cls, '__members__'):
                logger.debug(f"类 {cls.__name__} 没有__members__属性")
                return False

            # 检查枚举实例是否有必要的属性
            for member in cls:
                logger.debug(f"检查枚举成员 {cls.__name__}.{member.name}")
                has_value_code = hasattr(member, 'value_code')
                has_description = hasattr(member, 'description')
                logger.debug(f"  has_value_code={has_value_code}, has_description={has_description}")
                if has_value_code and has_description:
                    logger.debug(f"类 {cls.__name__} 是BaseEnum")
                    return True

            logger.debug(f"类 {cls.__name__} 的成员没有value_code和description属性")
            return False

        except Exception as e:
            logger.debug(f"检查类失败: {e}")
            return False

    def _to_enum_dict(self, enum_class) -> List[Dict[str, Any]]:
        """
        将枚举转换为枚举字典（一比一复刻 toEnumDict()）

        一比一复刻参考项目:
        return Arrays.stream(enumConstants).map(e -> {
            BaseEnum baseEnum = (BaseEnum)e;
            return new LabelValueResp(baseEnum.getDescription(), baseEnum.getValue(), baseEnum.getColor());
        }).toList();

        Args:
            enum_class: 枚举类

        Returns:
            List[Dict[str, Any]]: 枚举字典
        """
        try:
            result = []
            for member in enum_class:
                # 一比一复刻 LabelValueResp(description, value, color)
                item = {
                    "label": member.description,  # 对应 getDescription()
                    "value": member.value_code    # 对应 getValue()
                }

                # 如果有color属性，添加color（一比一复刻）
                if hasattr(member, 'color'):
                    item["color"] = member.color

                result.append(item)

            return result

        except Exception as e:
            logger.error(f"转换枚举字典失败 {enum_class}: {e}", exc_info=True)
            return []

    def _to_underline_case(self, camel_case: str) -> str:
        """
        驼峰转下划线（一比一复刻 StrUtil.toUnderlineCase()）

        Args:
            camel_case: 驼峰命名

        Returns:
            str: 下划线命名
        """
        result = []
        for i, char in enumerate(camel_case):
            if char.isupper():
                if i > 0:
                    result.append('_')
                result.append(char.lower())
            else:
                result.append(char)
        return ''.join(result)

    def list_enum_dict_names(self) -> List[str]:
        """
        列出所有枚举字典名称（一比一复刻 listEnumDictNames()）

        Returns:
            List[str]: 枚举字典名称列表
        """
        return list(self._ENUM_DICT_CACHE.keys())

    # ==================== CRUD 方法框架 ====================

    async def page(self, query, page: int, size: int):
        """
        分页查询字典项

        Args:
            query: 查询条件（DictItemQuery）
            page: 页码
            size: 每页大小

        Returns:
            PageResp: 分页结果
        """
        try:
            from apps.common.models.page_resp import PageResp
            from apps.system.core.model.resp.dict_item_resp import DictItemResp
            from sqlalchemy import func

            async with DatabaseSession.get_session_context() as session:
                # 构建查询条件
                stmt = select(DictItemEntity)

                # 关键词搜索
                if query.description:
                    search_pattern = f"%{query.description}%"
                    stmt = stmt.where(
                        (DictItemEntity.label.like(search_pattern)) |
                        (DictItemEntity.value.like(search_pattern)) |
                        (DictItemEntity.description.like(search_pattern))
                    )

                # 状态筛选
                if query.status is not None:
                    stmt = stmt.where(DictItemEntity.status == query.status)

                # 字典ID筛选
                if query.dict_id is not None:
                    stmt = stmt.where(DictItemEntity.dict_id == query.dict_id)

                # 查询总数
                count_stmt = select(func.count()).select_from(stmt.subquery())
                count_result = await session.execute(count_stmt)
                total = count_result.scalar()

                # 分页查询
                stmt = stmt.order_by(DictItemEntity.sort.asc())
                stmt = stmt.offset((page - 1) * size).limit(size)

                result = await session.execute(stmt)
                entities = result.scalars().all()

                # 转换为响应对象
                item_list = [
                    DictItemResp(
                        id=entity.id,
                        label=entity.label,
                        value=entity.value,
                        color=entity.color,
                        status=entity.status,
                        sort=entity.sort,
                        description=entity.description,
                        dict_id=entity.dict_id,
                        create_user_string=str(entity.create_user) if entity.create_user else None,
                        create_time=entity.create_time,
                        update_user_string=str(entity.update_user) if entity.update_user else None,
                        update_time=entity.update_time
                    )
                    for entity in entities
                ]

                # 计算总页数
                import math
                pages = math.ceil(total / size) if size > 0 else 0

                return PageResp(
                    list=item_list,
                    total=total,
                    current=page,
                    size=size,
                    pages=pages
                )

        except Exception as e:
            logger.error(f"分页查询字典项失败: {e}", exc_info=True)
            raise

    async def get(self, item_id: int):
        """
        查询字典项详情

        Args:
            item_id: 字典项ID

        Returns:
            DictItemResp: 字典项详情
        """
        try:
            from apps.system.core.model.resp.dict_item_resp import DictItemResp
            from apps.common.config.exception.global_exception_handler import BusinessException

            async with DatabaseSession.get_session_context() as session:
                stmt = select(DictItemEntity).where(DictItemEntity.id == item_id)
                result = await session.execute(stmt)
                entity = result.scalar_one_or_none()

                if entity is None:
                    raise BusinessException(f"字典项不存在 [ID: {item_id}]")

                return DictItemResp(
                    id=entity.id,
                    label=entity.label,
                    value=entity.value,
                    color=entity.color,
                    status=entity.status,
                    sort=entity.sort,
                    description=entity.description,
                    dict_id=entity.dict_id,
                    create_user_string=str(entity.create_user) if entity.create_user else None,
                    create_time=entity.create_time,
                    update_user_string=str(entity.update_user) if entity.update_user else None,
                    update_time=entity.update_time
                )

        except Exception as e:
            logger.error(f"查询字典项详情失败 [ID: {item_id}]: {e}", exc_info=True)
            raise

    async def create(self, req) -> int:
        """
        创建字典项

        Args:
            req: 创建请求（DictItemReq）

        Returns:
            int: 字典项ID
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 获取当前用户ID
                current_user_id = UserContextHolder.get_user_id()
                if current_user_id is None:
                    current_user_id = 1  # 如果未登录，默认使用1（超级管理员）

                # 创建实体
                entity = DictItemEntity(
                    label=req.label,
                    value=req.value,
                    color=req.color,
                    status=req.status,
                    sort=req.sort,
                    description=req.description,
                    dict_id=req.dict_id,
                    create_user=current_user_id
                )

                session.add(entity)
                await session.flush()

                logger.info(f"创建字典项成功 [ID: {entity.id}, 标签: {req.label}, 字典ID: {req.dict_id}]")
                return entity.id

        except Exception as e:
            logger.error(f"创建字典项失败 [标签: {req.label}]: {e}", exc_info=True)
            raise

    async def update(self, item_id: int, req) -> None:
        """
        更新字典项

        Args:
            item_id: 字典项ID
            req: 更新请求（DictItemReq）
        """
        try:
            from apps.common.config.exception.global_exception_handler import BusinessException

            async with DatabaseSession.get_session_context() as session:
                # 获取当前用户ID
                current_user_id = UserContextHolder.get_user_id()
                if current_user_id is None:
                    current_user_id = 1  # 如果未登录，默认使用1（超级管理员）

                # 查询字典项
                stmt = select(DictItemEntity).where(DictItemEntity.id == item_id)
                result = await session.execute(stmt)
                entity = result.scalar_one_or_none()

                if entity is None:
                    raise BusinessException(f"字典项不存在 [ID: {item_id}]")

                # 更新字段
                entity.label = req.label
                entity.value = req.value
                entity.color = req.color
                entity.status = req.status
                entity.sort = req.sort
                entity.description = req.description
                entity.dict_id = req.dict_id
                entity.update_user = current_user_id

                await session.flush()

                logger.info(f"更新字典项成功 [ID: {item_id}, 标签: {req.label}]")

        except Exception as e:
            logger.error(f"更新字典项失败 [ID: {item_id}]: {e}", exc_info=True)
            raise

    async def batch_delete(self, ids: List[int]) -> None:
        """
        批量删除字典项

        Args:
            ids: 字典项ID列表
        """
        try:
            from apps.common.config.exception.global_exception_handler import BusinessException

            async with DatabaseSession.get_session_context() as session:
                # 查询要删除的字典项
                stmt = select(DictItemEntity).where(DictItemEntity.id.in_(ids))
                result = await session.execute(stmt)
                entities = result.scalars().all()

                if not entities:
                    raise BusinessException("未找到要删除的字典项")

                # 删除字典项
                for entity in entities:
                    await session.delete(entity)

                await session.flush()

                logger.info(f"批量删除字典项成功 [IDs: {ids}]")

        except Exception as e:
            logger.error(f"批量删除字典项失败 [IDs: {ids}]: {e}", exc_info=True)
            raise

    async def delete_by_dict_ids(self, dict_ids: List[int]) -> None:
        """
        根据字典ID删除字典项（级联删除）

        Args:
            dict_ids: 字典ID列表
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 查询要删除的字典项
                stmt = select(DictItemEntity).where(DictItemEntity.dict_id.in_(dict_ids))
                result = await session.execute(stmt)
                entities = result.scalars().all()

                if entities:
                    # 删除字典项
                    for entity in entities:
                        await session.delete(entity)

                    await session.flush()

                    logger.info(f"根据字典ID级联删除字典项成功 [字典IDs: {dict_ids}, 删除了{len(entities)}个字典项]")
                else:
                    logger.info(f"根据字典ID未找到需要删除的字典项 [字典IDs: {dict_ids}]")

        except Exception as e:
            logger.error(f"根据字典ID删除字典项失败 [字典IDs: {dict_ids}]: {e}", exc_info=True)
            raise


# 全局服务实例
_dict_item_service = None


def get_dict_item_service() -> DictItemService:
    """
    获取字典项服务实例

    Returns:
        DictItemService: 字典项服务实例
    """
    global _dict_item_service
    if _dict_item_service is None:
        _dict_item_service = DictItemService()
    return _dict_item_service