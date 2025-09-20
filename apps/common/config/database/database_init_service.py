# -*- coding: utf-8 -*-
"""
数据库初始化服务 - 直接执行参考项目的SQL文件
"""

from pathlib import Path
from sqlalchemy import text
from apps.common.config.database.database_session import DatabaseSession
from apps.common.config.logging import get_logger


class DatabaseInitService:
    """数据库初始化服务 - 直接执行参考项目的SQL文件"""

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

        # 获取SQLite SQL文件路径
        self.project_root = Path(__file__).parent.parent.parent.parent.parent
        self.sql_base_path = self.project_root / "db/sqlite"

    async def init_database(self, force_reinit: bool = False) -> bool:
        """
        初始化数据库 - 执行参考项目的数据初始化

        Args:
            force_reinit: 是否强制重新初始化

        Returns:
            bool: 初始化是否成功
        """
        try:
            if not force_reinit and await self._check_database_initialized():
                self.logger.info("🎯 数据库已初始化，跳过初始化过程")
                return True

            self.logger.info("🚀 开始数据库初始化（执行数据填充）...")

            # 直接执行数据初始化（表结构已经由ORM创建）
            if not await self._execute_sql_file("data.sql"):
                self.logger.error("❌ 数据初始化失败")
                return False

            self.logger.info("✅ 数据库初始化完成")
            return True

        except Exception as e:
            self.logger.error(f"❌ 数据库初始化过程中发生异常: {str(e)}", exc_info=True)
            return False

    async def _check_database_initialized(self) -> bool:
        """
        检查数据库是否已初始化
        通过检查关键表是否存在以及是否有足够数据来判断

        Returns:
            bool: 数据库是否已初始化
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 检查关键表是否存在且有足够数据
                tables_to_check = [
                    ("sys_menu", 30),  # 至少30个菜单
                    ("sys_user", 5),  # 至少5个用户
                    ("sys_dept", 5),  # 至少5个部门
                    ("sys_role", 3),  # 至少3个角色
                ]

                for table_name, min_count in tables_to_check:
                    # 检查表是否存在
                    result = await session.execute(
                        text(f"""
                        SELECT COUNT(*) as count
                        FROM sqlite_master
                        WHERE type='table'
                        AND name = '{table_name}'
                    """)
                    )

                    table_exists = result.fetchone()[0] > 0
                    if not table_exists:
                        self.logger.debug(f"表 {table_name} 不存在")
                        return False

                    # 检查是否有足够数据
                    result = await session.execute(
                        text(f"SELECT COUNT(*) as count FROM {table_name}")
                    )
                    data_count = result.fetchone()[0]

                    if data_count < min_count:
                        self.logger.debug(
                            f"表 {table_name} 数据不足: {data_count}/{min_count}"
                        )
                        return False

                self.logger.debug("所有关键表数据检查通过")
                return True

        except Exception as e:
            self.logger.debug(f"检查数据库初始化状态时发生异常: {str(e)}")
            return False

    async def _execute_sql_file(self, filename: str) -> bool:
        """
        执行SQL文件

        Args:
            filename: SQL文件名

        Returns:
            bool: 执行是否成功
        """
        sql_file_path = self.sql_base_path / filename

        if not sql_file_path.exists():
            self.logger.error(f"❌ SQL文件不存在: {sql_file_path}")
            return False

        try:
            self.logger.info(f"📄 执行SQL文件: {filename}")

            # 读取SQL文件内容
            with open(sql_file_path, "r", encoding="utf-8") as f:
                sql_content = f.read()

            # SQLite SQL文件已经是兼容格式，只需要简单清理
            sql_content = self._clean_sqlite_sql_content(sql_content)

            # 分割SQL语句并执行
            async with DatabaseSession.get_session_context() as session:
                # 智能分割SQL语句 - 按INSERT语句分割
                statements = self._split_sql_statements(sql_content)

                successful_statements = 0
                failed_statements = 0

                for i, statement in enumerate(statements):
                    if statement and not statement.strip().startswith("--"):
                        try:
                            # 不再输出具体SQL语句内容，只记录执行进度
                            await session.execute(text(statement))
                            successful_statements += 1
                        except Exception as e:
                            error_msg = str(e).lower()
                            # 可忽略的错误类型
                            ignorable_errors = [
                                "already exists",
                                "duplicate",
                                "constraint failed",
                                "unique constraint",
                                "primary key",
                                "not null constraint",
                            ]

                            is_ignorable = any(
                                err in error_msg for err in ignorable_errors
                            )

                            if is_ignorable:
                                # 数据重复冲突是正常的，静默处理
                                failed_statements += 1
                            else:
                                # 只输出错误的SQL语句开头部分，不输出完整语句
                                sql_preview = statement[:100] + "..." if len(statement) > 100 else statement
                                self.logger.error(f"❌ SQL语句 {i + 1} 执行失败: {str(e)}")
                                self.logger.error(f"失败的SQL语句预览: {sql_preview}")
                                failed_statements += 1
                                # 严重错误也不中断，继续执行其他语句
                                continue

                await session.commit()

                # 简化统计信息，只有真正的错误才报告
                if failed_statements > 0 and successful_statements == 0:
                    self.logger.warning(f"SQL file {filename}: all statements failed")
                elif successful_statements > 0:
                    self.logger.info(f"SQL file {filename}: {successful_statements} statements executed successfully")

                # 只要有一半以上语句成功就认为初始化成功
                if (
                    successful_statements > 0
                    and successful_statements >= len(statements) * 0.5
                ):
                    self.logger.info(f"SQL file {filename} execution completed successfully")
                    return True
                else:
                    self.logger.warning(f"SQL file {filename} had low success rate: {successful_statements}/{len(statements)}")
                    return successful_statements > 0  # 只要有成功的语句就返回True

        except Exception as e:
            self.logger.error(f"Failed to execute SQL file {filename}: {str(e)}")
            return False

    def _clean_sqlite_sql_content(self, sql_content: str) -> str:
        """
        清理SQLite SQL内容，移除注释和空行

        Args:
            sql_content: 原始SQL内容

        Returns:
            str: 清理后的SQL内容
        """
        lines = sql_content.split("\n")
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            # 跳过注释和空行
            if line.startswith("--") or not line:
                continue
            cleaned_lines.append(line)

        return "\n".join(cleaned_lines)

    def _split_sql_statements(self, sql_content: str) -> list:
        """
        分割SQLite SQL语句
        按分号分割，适用于SQLite SQL格式

        Args:
            sql_content: SQL内容

        Returns:
            list: 分割后的SQL语句列表
        """
        statements = []

        # 按分号分割，但要考虑字符串中的分号
        current_statement = ""
        in_single_quote = False
        in_double_quote = False

        i = 0
        while i < len(sql_content):
            char = sql_content[i]

            if char == "'" and not in_double_quote:
                in_single_quote = not in_single_quote
            elif char == '"' and not in_single_quote:
                in_double_quote = not in_double_quote
            elif char == ";" and not in_single_quote and not in_double_quote:
                # 找到语句结束
                statement = current_statement.strip()
                if statement and not statement.startswith("--") and len(statement) > 5:
                    statements.append(statement)
                current_statement = ""
                i += 1
                continue

            current_statement += char
            i += 1

        # 添加最后一个语句（如果没有分号结尾）
        statement = current_statement.strip()
        if statement and not statement.startswith("--") and len(statement) > 5:
            statements.append(statement)

        return statements

    async def _remove_existing_database(self) -> bool:
        """
        删除现有数据库文件（用于强制重新初始化）

        Returns:
            bool: 删除是否成功
        """
        try:
            # 获取数据库文件路径
            from apps.common.config.database.database_config import get_database_config
            db_config = get_database_config()

            # 从DATABASE_URL中提取SQLite数据库文件路径
            if "sqlite" in db_config.url.lower():
                # 解析sqlite:///path/to/database.db格式
                import re
                match = re.search(r'sqlite.*:///(.*)', db_config.url)
                if match:
                    db_file_path = Path(match.group(1))
                    if db_file_path.exists():
                        db_file_path.unlink()
                        self.logger.info(f"🗑️ 已删除数据库文件: {db_file_path}")
                        return True

            return True
        except Exception as e:
            self.logger.warning(f"⚠️ 删除数据库文件失败: {str(e)}")
            return False

    async def _create_tables_with_orm(self) -> bool:
        """
        使用SQLAlchemy ORM创建表结构

        Returns:
            bool: 创建是否成功
        """
        try:
            from apps.common.config.database import create_tables

            # 使用已有的create_tables方法创建所有表
            await create_tables()

            self.logger.info("✅ SQLAlchemy ORM表结构创建完成")
            return True

        except Exception as e:
            self.logger.error(f"❌ SQLAlchemy ORM表结构创建失败: {str(e)}", exc_info=True)
            return False

    async def reset_database(self) -> bool:
        """
        重置数据库（删除所有系统表）
        谨慎使用！

        Returns:
            bool: 重置是否成功
        """
        try:
            self.logger.warning("🔥 开始重置数据库...")

            async with DatabaseSession.get_session_context() as session:
                # 获取所有系统表名
                result = await session.execute(
                    text("""
                    SELECT name FROM sqlite_master
                    WHERE type='table'
                    AND name LIKE 'sys_%'
                """)
                )

                tables = [row[0] for row in result.fetchall()]

                # 删除所有系统表
                for table in tables:
                    await session.execute(text(f"DROP TABLE IF EXISTS {table}"))
                    self.logger.info(f"🗑️ 删除表: {table}")

                await session.commit()

            self.logger.warning("✅ 数据库重置完成")
            return True

        except Exception as e:
            self.logger.error(f"❌ 数据库重置失败: {str(e)}", exc_info=True)
            return False