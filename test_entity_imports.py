#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试所有实体类导入
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_entity_imports():
    """Test entity import"""
    print("Testing all entity imports...")

    entity_files = [
        'apps.system.core.model.entity.user_entity',
        'apps.system.core.model.entity.role_entity',
        'apps.system.core.model.entity.menu_entity',
        'apps.system.core.model.entity.dept_entity',
        'apps.system.core.model.entity.user_role_entity',
        'apps.system.core.model.entity.role_menu_entity',
        'apps.system.core.model.entity.role_dept_entity',
        'apps.system.core.model.entity.client_entity',
        'apps.system.core.model.entity.option_entity',
        'apps.system.core.model.entity.dict_entity',
        'apps.system.core.model.entity.dict_item_entity',
        'apps.system.core.model.entity.storage_entity',
        'apps.system.core.model.entity.user_password_history_entity',
        'apps.system.core.model.entity.user_social_entity',
        'apps.system.core.model.entity.log_entity',
        'apps.system.core.model.entity.message_entity',
        'apps.system.core.model.entity.message_log_entity',
        'apps.system.core.model.entity.notice_entity',
        'apps.system.core.model.entity.notice_log_entity',
        'apps.system.core.model.entity.file_entity',
        'apps.system.core.model.entity.sms_config_entity',
        'apps.system.core.model.entity.sms_log_entity'
    ]

    success_count = 0
    failed_imports = []

    for entity_module in entity_files:
        try:
            __import__(entity_module)
            print(f"OK {entity_module}")
            success_count += 1
        except ImportError as e:
            print(f"FAIL {entity_module}: {e}")
            failed_imports.append((entity_module, str(e)))

    print(f"\nImport results: {success_count}/{len(entity_files)} successful")

    if failed_imports:
        print("\nFailed imports:")
        for module, error in failed_imports:
            print(f"  - {module}: {error}")
        return False
    else:
        print("All entity imports successful!")
        return True

def test_models_registration():
    """Test models registration"""
    print("\nTesting models registration...")

    try:
        from apps.common.config.database.models import get_all_models, validate_models

        models = get_all_models()
        print(f"Successfully registered {len(models)} models")

        for model in models:
            print(f"  - {model['name']:<35} -> {model['table_name']}")

        print("\nValidating model definitions...")
        is_valid = validate_models()

        return is_valid and len(models) == 22

    except Exception as e:
        print(f"Models registration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting entity import tests...\n")

    import_success = test_entity_imports()
    if import_success:
        models_success = test_models_registration()
        if models_success:
            print("\nAll tests passed! Database entities are ready.")
        else:
            print("\nModels registration test failed.")
    else:
        print("\nEntity import test failed.")