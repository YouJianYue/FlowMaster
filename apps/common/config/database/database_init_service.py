# -*- coding: utf-8 -*-
"""
数据库初始化服务 - 直接执行参考项目的SQL文件

@author: continew-admin
@since: 2025/9/14 14:00
"""

from pathlib import Path
from sqlalchemy import text
from apps.common.config.database.database_session import DatabaseSession
from apps.common.config.logging import get_logger


class DatabaseInitService:
    """数据库初始化服务 - 直接执行参考项目的SQL文件"""

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

        # 获取参考项目SQL文件路径
        self.project_root = Path(__file__).parent.parent.parent.parent.parent
        self.sql_base_path = self.project_root / "refrence/continew-admin/continew-server/src/main/resources/db/changelog/postgresql"

    async def init_database(self, force_reinit: bool = False) -> bool:
        """
        初始化数据库 - 直接执行参考项目的SQL文件

        Args:
            force_reinit: 是否强制重新初始化

        Returns:
            bool: 初始化是否成功
        """
        try:
            if not force_reinit and await self._check_database_initialized():
                self.logger.info("🎯 数据库已初始化，跳过初始化过程")
                return True

            self.logger.info("🚀 开始数据库初始化（使用参考项目SQL文件）...")

            # 1. 执行表结构初始化
            if not await self._execute_sql_file("main_table.sql"):
                self.logger.error("❌ 表结构初始化失败")
                return False

            # 2. 执行数据初始化
            if not await self._execute_sql_file("main_data.sql"):
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
        通过检查关键表是否存在以及是否有数据来判断

        Returns:
            bool: 数据库是否已初始化
        """
        try:
            async with DatabaseSession.get_session_context() as session:
                # 检查sys_menu表是否存在且有数据（SQLite语法）
                result = await session.execute(text("""
                    SELECT COUNT(*) as count
                    FROM sqlite_master
                    WHERE type='table'
                    AND name = 'sys_menu'
                """))

                table_exists = result.fetchone()[0] > 0

                if table_exists:
                    # 检查是否有菜单数据
                    result = await session.execute(text("SELECT COUNT(*) as count FROM sys_menu"))
                    data_count = result.fetchone()[0]
                    return data_count > 0

                return False

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
            with open(sql_file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()

            # 清理SQL内容，移除liquibase相关注释
            sql_content = self._clean_sql_content(sql_content)

            # 替换PostgreSQL特定语法为SQLite兼容语法
            sql_content = self._convert_postgresql_to_sqlite(sql_content)

            # 分割SQL语句并执行
            async with DatabaseSession.get_session_context() as session:
                # 智能分割SQL语句 - 按INSERT语句分割
                statements = self._split_sql_statements(sql_content)

                for i, statement in enumerate(statements):
                    if statement and not statement.strip().startswith('--'):
                        try:
                            self.logger.debug(f"✓ 执行第{i+1}个SQL语句: {statement[:100]}...")
                            await session.execute(text(statement))
                        except Exception as e:
                            # 如果是表已存在等可忽略的错误，记录警告但继续执行
                            if ("already exists" in str(e).lower() or
                                "duplicate" in str(e).lower() or
                                "constraint" in str(e).lower()):
                                self.logger.warning(f"⚠️ SQL语句执行警告（已忽略）: {str(e)}")
                            else:
                                self.logger.error(f"❌ SQL语句执行失败: {str(e)}")
                                self.logger.error(f"失败的SQL语句: {statement}")
                                raise

                await session.commit()

            self.logger.info(f"✅ SQL文件执行完成: {filename}")
            return True

        except Exception as e:
            self.logger.error(f"❌ 执行SQL文件 {filename} 失败: {str(e)}", exc_info=True)
            return False

    def _clean_sql_content(self, sql_content: str) -> str:
        """
        清理SQL内容，移除liquibase格式化注释

        Args:
            sql_content: 原始SQL内容

        Returns:
            str: 清理后的SQL内容
        """
        lines = sql_content.split('\n')
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            # 跳过liquibase格式化注释
            if (line.startswith('-- liquibase formatted sql') or
                line.startswith('-- changeset') or
                line.startswith('-- comment') or
                line == '--' or
                not line):
                continue
            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _split_sql_statements(self, sql_content: str) -> list:
        """
        智能分割SQL语句
        处理复杂的INSERT语句，避免在VALUES中间分割

        Args:
            sql_content: SQL内容

        Returns:
            list: 分割后的SQL语句列表
        """
        import re

        statements = []
        current_statement = ""
        lines = sql_content.split('\n')

        for line in lines:
            line = line.strip()
            if not line or line.startswith('--'):
                continue

            current_statement += line + "\n"

            # 检查是否是完整的语句
            if line.endswith(';'):
                # 移除结尾的分号
                current_statement = current_statement.rstrip(';\n').strip()
                if current_statement:
                    statements.append(current_statement)
                current_statement = ""
            elif (line.startswith('CREATE') or
                  line.startswith('INSERT') or
                  line.startswith('UPDATE') or
                  line.startswith('DELETE')):
                # 如果当前有未完成的语句，先保存
                if current_statement.strip() and not current_statement.strip().endswith(line):
                    prev_statement = current_statement.replace(line + "\n", "").strip()
                    if prev_statement:
                        statements.append(prev_statement)
                # 开始新语句
                current_statement = line + "\n"

        # 处理最后一个语句
        if current_statement.strip():
            current_statement = current_statement.rstrip(';\n').strip()
            if current_statement:
                statements.append(current_statement)

        return statements

    def _convert_postgresql_to_sqlite(self, sql_content: str) -> str:
        """
        将PostgreSQL语法转换为SQLite兼容语法

        Args:
            sql_content: PostgreSQL SQL内容

        Returns:
            str: SQLite兼容的SQL内容
        """
        import re

        # 处理复杂的语法转换，按顺序进行
        result = sql_content

        # 1. 处理CREATE TABLE语句中的双引号
        result = re.sub(r'CREATE TABLE IF NOT EXISTS "([^"]+)"', r'CREATE TABLE IF NOT EXISTS \1', result)

        # 2. 处理字段定义中的双引号
        result = re.sub(r'"([^"]+)"\s+', r'\1 ', result)

        # 3. 数据类型转换
        type_conversions = [
            (r'\bint8\b', 'INTEGER'),
            (r'\bint4\b', 'INTEGER'),
            (r'\bint2\b', 'INTEGER'),
            (r'\bbool\b', 'BOOLEAN'),
            (r'varchar\(\d+\)', 'TEXT'),
            (r'\btext\b', 'TEXT'),
            (r'\btimestamp\b', 'DATETIME'),
            (r'\bjson\b', 'TEXT'),
        ]

        for old_pattern, new_type in type_conversions:
            result = re.sub(old_pattern, new_type, result)

        # 4. 时间函数转换 - 使用SQLite的CURRENT_TIMESTAMP
        result = result.replace('NOW()', 'CURRENT_TIMESTAMP')
        result = result.replace('datetime(now)', 'CURRENT_TIMESTAMP')
        result = result.replace('datetime("now")', 'CURRENT_TIMESTAMP')

        # 5. 布尔值转换
        result = result.replace(' false', ' 0')
        result = result.replace(' true', ' 1')
        result = result.replace(' false,', ' 0,')
        result = result.replace(' true,', ' 1,')

        # 6. 处理PRIMARY KEY约束
        result = re.sub(r'PRIMARY KEY \("([^"]+)"\)', r'PRIMARY KEY (\1)', result)

        # 7. 处理INDEX语句
        result = re.sub(r'CREATE INDEX "([^"]+)" ON "([^"]+)" \("([^"]+)"\)',
                       r'CREATE INDEX IF NOT EXISTS \1 ON \2 (\3)', result)
        result = re.sub(r'CREATE UNIQUE INDEX "([^"]+)" ON "([^"]+)" \("([^"]+)"\)',
                       r'CREATE UNIQUE INDEX IF NOT EXISTS \1 ON \2 (\3)', result)
        result = re.sub(r'CREATE INDEX "([^"]+)" ON "([^"]+)" \("([^"]+)", "([^"]+)"\)',
                       r'CREATE INDEX IF NOT EXISTS \1 ON \2 (\3, \4)', result)
        result = re.sub(r'CREATE UNIQUE INDEX "([^"]+)" ON "([^"]+)" \("([^"]+)", "([^"]+)"\)',
                       r'CREATE UNIQUE INDEX IF NOT EXISTS \1 ON \2 (\3, \4)', result)

        # 8. 处理INSERT语句中的双引号
        result = re.sub(r'INSERT INTO "([^"]+)"', r'INSERT INTO \1', result)
        # 处理INSERT语句中字段列表的双引号
        result = re.sub(r'\("([^"]+)"', r'(\1', result)
        result = re.sub(r', "([^"]+)"', r', \1', result)
        result = re.sub(r'"([^"]+)"\)', r'\1)', result)

        # 9. 注释语法转换（SQLite不支持COMMENT ON）
        result = re.sub(r'COMMENT ON COLUMN[^;]*;', '', result)
        result = re.sub(r'COMMENT ON TABLE[^;]*;', '', result)

        # 10. 清理多余的空行
        result = re.sub(r'\n\s*\n', '\n', result)

        return result

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
                result = await session.execute(text("""
                    SELECT name FROM sqlite_master
                    WHERE type='table'
                    AND name LIKE 'sys_%'
                """))

                tables = [row[0] for row in result.fetchall()]

                # 删除所有系统表
                for table in tables:
                    await session.execute(text(f'DROP TABLE IF EXISTS {table}'))
                    self.logger.info(f"🗑️ 删除表: {table}")

                await session.commit()

            self.logger.warning("✅ 数据库重置完成")
            return True

        except Exception as e:
            self.logger.error(f"❌ 数据库重置失败: {str(e)}", exc_info=True)
            return False