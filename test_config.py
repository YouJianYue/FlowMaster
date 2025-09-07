# -*- coding: utf-8 -*-

"""
配置文件测试脚本
"""

import asyncio
import os
from apps.common.config.database import (
    database_config, 
    DatabaseSession, 
    init_database,
    check_db_status
)
from apps.common.config.logging import setup_logging, get_logger

async def test_database_config():
    """测试数据库配置"""
    print("🔧 测试数据库配置...")
    
    # 显示配置信息
    print(f"  数据库类型: {database_config.get_database_type()}")
    print(f"  数据库URL: {database_config.url}")
    print(f"  连接池大小: {database_config.pool_size}")
    print(f"  SQL回显: {database_config.echo}")
    
    try:
        # 测试数据库连接
        print("\n📡 测试数据库连接...")
        await init_database()
        print("  ✅ 数据库初始化成功")
        
        # 检查数据库状态
        status = await check_db_status()
        print(f"  📊 数据库状态: {status}")
        
    except Exception as e:
        print(f"  ❌ 数据库配置测试失败: {e}")

def test_logging_config():
    """测试日志配置"""
    print("\n📝 测试日志配置...")
    
    # 设置日志
    setup_logging()
    
    # 获取不同类型的logger
    main_logger = get_logger("test.main")
    auth_logger = get_logger("test.auth")
    
    # 测试各级别日志
    print("  测试日志输出...")
    main_logger.debug("这是 DEBUG 级别日志")
    main_logger.info("这是 INFO 级别日志")
    main_logger.warning("这是 WARNING 级别日志")
    main_logger.error("这是 ERROR 级别日志")
    
    auth_logger.info("认证模块日志测试")
    
    print("  ✅ 日志配置测试完成")

def test_environment_variables():
    """测试环境变量加载"""
    print("\n🌍 测试环境变量...")
    
    # 检查关键环境变量
    env_vars = [
        "DATABASE_URL",
        "LOG_LEVEL", 
        "JWT_SECRET_KEY",
        "ENVIRONMENT"
    ]
    
    for var in env_vars:
        value = os.getenv(var, "未设置")
        # 对于敏感信息，只显示前几个字符
        if "SECRET" in var or "PASSWORD" in var:
            value = f"{value[:10]}..." if len(value) > 10 else value
        print(f"  {var}: {value}")

async def main():
    """主测试函数"""
    print("🚀 FlowMaster 配置文件测试\n")
    
    # 测试环境变量
    test_environment_variables()
    
    # 测试日志配置
    test_logging_config()
    
    # 测试数据库配置
    await test_database_config()
    
    print("\n✨ 所有配置测试完成!")

if __name__ == "__main__":
    asyncio.run(main())