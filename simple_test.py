# -*- coding: utf-8 -*-

"""
简化的配置文件测试脚本
"""

import os
import sys

def test_environment_variables():
    """测试环境变量加载"""
    print("🌍 测试环境变量...")
    
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
            if value != "未设置" and len(value) > 10:
                value = f"{value[:10]}..."
        print(f"  {var}: {value}")

def test_pydantic_import():
    """测试Pydantic导入"""
    print("\n📦 测试Pydantic导入...")
    
    try:
        from pydantic import Field, model_validator
        from pydantic_settings import BaseSettings, SettingsConfigDict
        print("  ✅ Pydantic v2导入成功")
        return True
    except ImportError as e:
        print(f"  ❌ Pydantic导入失败: {e}")
        return False

def test_database_config_class():
    """测试数据库配置类"""
    print("\n🔧 测试数据库配置类...")
    
    try:
        # 临时添加当前目录到Python路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        from apps.common.config.database.database_config import DatabaseConfig
        
        # 创建配置实例
        config = DatabaseConfig()
        print(f"  数据库类型: {config.get_database_type()}")
        print(f"  数据库URL: {config.url}")
        print(f"  连接池大小: {config.pool_size}")
        print(f"  SQL回显: {config.echo}")
        print(f"  连接参数: {config.connect_args}")
        print("  ✅ 数据库配置类测试成功")
        return True
    except Exception as e:
        print(f"  ❌ 数据库配置类测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 FlowMaster 配置文件兼容性测试\n")
    
    # 检查.env文件是否存在
    if os.path.exists('.env'):
        print("📋 找到.env配置文件")
    else:
        print("⚠️  .env配置文件不存在，将使用默认值")
    
    # 测试环境变量
    test_environment_variables()
    
    # 测试Pydantic导入
    pydantic_ok = test_pydantic_import()
    
    if pydantic_ok:
        # 测试数据库配置类
        test_database_config_class()
    else:
        print("\n⚠️  由于Pydantic导入失败，跳过配置类测试")
        print("   请运行: pip install -r requirements.txt")
    
    print("\n✨ 兼容性测试完成!")
    
    if not pydantic_ok:
        print("\n🔧 后续步骤:")
        print("   1. 安装依赖: pip install -r requirements.txt")
        print("   2. 重新运行测试: python simple_test.py")

if __name__ == "__main__":
    main()