# -*- coding: utf-8 -*-
"""
部门数据初始化服务
"""

from typing import List
from sqlalchemy import select, func
from datetime import datetime

from apps.system.core.model.entity.dept_entity import DeptEntity
from apps.common.config.database.database_session import DatabaseSession
from apps.common.config.logging import get_logger


class DeptInitService:
    """部门数据初始化服务"""

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    async def init_dept_data(self) -> None:
        """
        初始化部门数据

        如果数据库中没有部门数据，则插入初始化数据
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 检查是否已有部门数据
                result = await session.execute(select(func.count(DeptEntity.id)))
                count = result.scalar_one()

                if count > 0:
                    self.logger.info(f"部门表已有 {count} 条数据，跳过初始化")
                    return

                self.logger.info("开始初始化部门数据...")

                # 获取初始化数据
                init_data = self._get_init_dept_data()

                # 批量插入
                session.add_all(init_data)
                await session.commit()

                self.logger.info(f"成功初始化 {len(init_data)} 条部门数据")

        except Exception as e:
            self.logger.error(f"部门数据初始化失败: {e}")
            raise

    def _get_init_dept_data(self) -> List[DeptEntity]:
        """获取初始化部门数据"""
        current_time = datetime.now()

        return [
            # 1. 根部门
            DeptEntity(
                id=1,
                name="FlowMaster科技有限公司",
                parent_id=0,  # 根部门parent_id应为0
                ancestors="0",  # 根部门ancestors为"0"
                description="系统初始部门",
                sort=1,
                status=1,
                is_system=True,  # 根部门是系统内置
                create_user=1,
                create_time=current_time,
                update_user=None,
                update_time=None
            ),

            # 2. 天津分公司
            DeptEntity(
                id=547887852587843590,
                name="FlowMaster（天津）科技有限公司",
                parent_id=1,
                ancestors="0,1",  # 参考项目格式：包含0前缀
                description=None,
                sort=1,
                status=1,
                is_system=False,
                create_user=1,
                create_time=current_time,
                update_user=None,
                update_time=None
            ),

            # 3. 天津-研发部
            DeptEntity(
                id=547887852587843591,
                name="研发部",
                parent_id=547887852587843590,
                ancestors="0,1,547887852587843590",  # 修正ancestors格式
                description=None,
                sort=1,
                status=1,
                is_system=False,
                create_user=1,
                create_time=current_time,
                update_user=None,
                update_time=None
            ),

            # 4. 天津-研发部-研发一组
            DeptEntity(
                id=547887852587843595,
                name="研发一组",
                parent_id=547887852587843591,
                ancestors="0,1,547887852587843590,547887852587843591",  # 修正ancestors格式
                description=None,
                sort=1,
                status=1,
                is_system=False,
                create_user=1,
                create_time=current_time,
                update_user=None,
                update_time=None
            ),

            # 5. 天津-研发部-研发二组
            DeptEntity(
                id=547887852587843596,
                name="研发二组",
                parent_id=547887852587843591,
                ancestors="0,1,547887852587843590,547887852587843591",  # 修正ancestors格式
                description=None,
                sort=2,
                status=2,  # 禁用状态
                is_system=False,
                create_user=1,
                create_time=current_time,
                update_user=None,
                update_time=None
            ),

            # 6. 天津-UI部
            DeptEntity(
                id=547887852587843592,
                name="UI部",
                parent_id=547887852587843590,
                ancestors="0,1,547887852587843590",
                description=None,
                sort=2,
                status=1,
                is_system=False,
                create_user=1,
                create_time=current_time,
                update_user=None,
                update_time=None
            ),

            # 7. 天津-测试部
            DeptEntity(
                id=547887852587843593,
                name="测试部",
                parent_id=547887852587843590,
                ancestors="0,1,547887852587843590",
                description=None,
                sort=3,
                status=1,
                is_system=False,
                create_user=1,
                create_time=current_time,
                update_user=None,
                update_time=None
            ),

            # 8. 天津-运维部
            DeptEntity(
                id=547887852587843594,
                name="运维部",
                parent_id=547887852587843590,
                ancestors="0,1,547887852587843590",
                description=None,
                sort=4,
                status=1,
                is_system=False,
                create_user=1,
                create_time=current_time,
                update_user=None,
                update_time=None
            ),

            # 9. 江西分公司
            DeptEntity(
                id=547887852587843600,
                name="FlowMaster（江西）科技有限公司",
                parent_id=1,
                ancestors="0,1",
                description=None,
                sort=3,
                status=1,
                is_system=False,
                create_user=1,
                create_time=current_time,
                update_user=None,
                update_time=None
            ),

            # 10. 江西-研发部
            DeptEntity(
                id=547887852587843601,
                name="研发部",
                parent_id=547887852587843600,
                ancestors="0,1,547887852587843600",
                description=None,
                sort=1,
                status=1,
                is_system=False,
                create_user=1,
                create_time=current_time,
                update_user=None,
                update_time=None
            ),

            # 11. 江西-研发一组
            DeptEntity(
                id=547887852587843602,
                name="研发一组",
                parent_id=547887852587843601,
                ancestors="0,1,547887852587843600,547887852587843601",
                description=None,
                sort=1,
                status=1,
                is_system=False,
                create_user=1,
                create_time=current_time,
                update_user=None,
                update_time=None
            )
        ]