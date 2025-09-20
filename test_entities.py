#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单的实体测试脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_entity_imports():
    """测试实体类导入"""
    print("🔍 Testing entity imports...")

    # 测试基础实体导入
    try:
        from apps.common.base.model.entity.base_entity import BaseEntity, Base
        print("✅ BaseEntity and Base imported successfully")
    except Exception as e:
        print(f"❌ BaseEntity import failed: {e}")
        return False

    # 测试简单实体导入
    try:
        from apps.system.core.model.entity.user_entity import UserEntity
        print("✅ UserEntity imported successfully")
    except Exception as e:
        print(f"❌ UserEntity import failed: {e}")
        return False

    # 测试新创建的实体导入
    try:
        from apps.system.core.model.entity.user_password_history_entity import UserPasswordHistoryEntity
        print("✅ UserPasswordHistoryEntity imported successfully")
    except Exception as e:
        print(f"❌ UserPasswordHistoryEntity import failed: {e}")
        return False

    print("✅ All entity imports successful!")
    return True

def test_models_registration():
    """测试模型注册"""
    print("\n🔍 Testing models registration...")

    try:
        from apps.common.config.database.models import get_all_models, validate_models

        models = get_all_models()
        print(f"✅ Successfully registered {len(models)} models")

        for model in models:
            print(f"  - {model['name']:<30} -> {model['table_name']}")

        print("\n🔍 Validating models...")
        is_valid = validate_models()

        if is_valid:
            print("✅ All models are valid!")
            return True
        else:
            print("❌ Some models have issues")
            return False

    except Exception as e:
        print(f"❌ Models registration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting entity tests...")

    if test_entity_imports():
        if test_models_registration():
            print("\n🎉 All tests passed! Database entities are ready.")
        else:
            print("\n❌ Model registration tests failed.")
    else:
        print("\n❌ Entity import tests failed.")