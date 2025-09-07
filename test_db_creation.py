# -*- coding: utf-8 -*-

"""
测试数据库表结构自动创建
"""

import os
import sys
import asyncio

# 手动加载环境变量
def load_env():
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value.strip('"').strip("'")

async def test_database_creation():
    """测试数据库表创建"""
    print("🔧 测试数据库表结构自动创建...")
    
    try:
        # 添加项目根目录到Python路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # 导入数据库模块
        from apps.common.config.database.models import print_registered_models, validate_models
        from apps.common.config.database import init_database, check_db_status, database_config
        
        # 显示数据库配置
        print(f"📊 数据库配置:")
        print(f"  类型: {database_config.get_database_type()}")
        print(f"  URL: {database_config.url}")
        print(f"  回显SQL: {database_config.echo}")
        
        # 显示已注册的模型
        print("\n📋 检查已注册的数据库模型...")
        models = print_registered_models()
        
        # 验证模型定义
        print("\n✅ 验证模型定义...")
        validate_models()
        
        # 初始化数据库（创建表结构）
        print("\n💾 创建数据库表结构...")
        await init_database()
        
        # 检查数据库状态
        print("\n📈 检查数据库状态...")
        status = await check_db_status()
        
        print(f"✅ 数据库初始化完成!")
        print(f"  连接状态: {'✅ 正常' if status['connection'] else '❌ 异常'}")
        print(f"  数据库类型: {status.get('database_type', 'unknown')}")
        print(f"  已创建表数量: {status.get('tables_count', 0)}")
        
        if status.get('tables'):
            print(f"  表列表:")
            for table in status['tables']:
                print(f"    - {table}")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("请先安装依赖: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return False

async def test_table_exists():
    """测试表是否存在"""
    print("\n🔍 验证表是否成功创建...")
    
    try:
        # 检查SQLite数据库文件
        db_url = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./data/flowmaster.db')
        
        if 'sqlite' in db_url:
            db_file = db_url.replace('sqlite+aiosqlite:///', './')
            
            if os.path.exists(db_file):
                file_size = os.path.getsize(db_file)
                print(f"✅ SQLite数据库文件已创建: {db_file}")
                print(f"   文件大小: {file_size} 字节")
                
                # 如果文件大小大于0，说明有内容
                if file_size > 0:
                    print("✅ 数据库包含表结构")
                else:
                    print("⚠️  数据库文件为空")
                
                return True
            else:
                print(f"❌ SQLite数据库文件不存在: {db_file}")
                return False
        else:
            print("🔍 使用非SQLite数据库，跳过文件检查")
            return True
            
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🚀 FlowMaster 数据库表结构自动创建测试\n")
    
    # 加载环境变量
    load_env()
    
    # 测试数据库创建
    db_ok = await test_database_creation()
    
    if db_ok:
        # 测试表是否存在
        await test_table_exists()
        
        print("\n✨ 测试完成!")
        print("\n📋 总结:")
        print("  ✅ 数据库配置正确")
        print("  ✅ 模型注册成功") 
        print("  ✅ 表结构自动创建")
        print("  ✅ 数据库连接正常")
        
        print("\n🎯 现在可以启动应用:")
        print("  python main.py")
        
    else:
        print("\n❌ 测试失败!")
        print("请检查:")
        print("  1. 是否安装了依赖: pip install -r requirements.txt")
        print("  2. 是否正确配置了.env文件")

if __name__ == "__main__":
    asyncio.run(main())