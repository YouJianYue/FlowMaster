# -*- coding: utf-8 -*-

"""
数据库模型注册模块 - 确保所有模型被SQLAlchemy识别
"""

# 导入数据库基类
from apps.common.base.model.entity.base_entity import Base

# ==========================================
# 导入所有实体类，确保它们被SQLAlchemy识别
# ==========================================

# 基础实体类（必须最先导入）

# 认证模块实体类

# 系统核心模块实体类
# 核心业务表（12个）
from apps.system.core.model.entity.user_entity import UserEntity  # noqa: F401
from apps.system.core.model.entity.role_entity import RoleEntity  # noqa: F401
from apps.system.core.model.entity.menu_entity import MenuEntity  # noqa: F401
from apps.system.core.model.entity.dept_entity import DeptEntity  # noqa: F401
from apps.system.core.model.entity.user_role_entity import UserRoleEntity  # noqa: F401
from apps.system.core.model.entity.role_menu_entity import RoleMenuEntity  # noqa: F401
from apps.system.core.model.entity.role_dept_entity import RoleDeptEntity  # noqa: F401
from apps.system.core.model.entity.client_entity import ClientEntity  # noqa: F401
from apps.system.core.model.entity.option_entity import OptionEntity  # noqa: F401
from apps.system.core.model.entity.dict_entity import DictEntity  # noqa: F401
from apps.system.core.model.entity.dict_item_entity import DictItemEntity  # noqa: F401
from apps.system.core.model.entity.storage_entity import StorageEntity  # noqa: F401

# 扩展功能表（10个）
from apps.system.core.model.entity.user_password_history_entity import UserPasswordHistoryEntity  # noqa: F401
from apps.system.core.model.entity.user_social_entity import UserSocialEntity  # noqa: F401
from apps.system.core.model.entity.log_entity import LogEntity  # noqa: F401
from apps.system.core.model.entity.message_entity import MessageEntity  # noqa: F401
from apps.system.core.model.entity.message_log_entity import MessageLogEntity  # noqa: F401
from apps.system.core.model.entity.notice_entity import NoticeEntity  # noqa: F401
from apps.system.core.model.entity.notice_log_entity import NoticeLogEntity  # noqa: F401
from apps.system.core.model.entity.file_entity import FileEntity  # noqa: F401
from apps.system.core.model.entity.sms_config_entity import SmsConfigEntity  # noqa: F401
from apps.system.core.model.entity.sms_log_entity import SmsLogEntity  # noqa: F401

# ==========================================
# 收集所有已注册的模型
# ==========================================

def get_all_models():
    """获取所有已注册的数据库模型"""
    model_list = []

    # 通过Base.registry._class_registry获取所有模型
    for mapper in Base.registry.mappers:
        model_class = mapper.class_
        model_list.append({
            'name': model_class.__name__,
            'table_name': getattr(model_class, '__tablename__', 'N/A'),
            'class': model_class
        })

    return model_list

def print_registered_models():
    """打印所有已注册的模型信息"""
    _models = get_all_models()
    
    # print("\n📋 已注册的数据库模型:")
    # print("-" * 60)
    # for i, model in enumerate(models, 1):
    #     print(f"{i:2d}. {model['name']:<20} -> {model['table_name']}")
    # print("-" * 60)
    # print(f"Total: {len(_models)} models")
    
    return _models

def get_table_names():
    """获取所有表名列表"""
    model_list = get_all_models()
    return [model['table_name'] for model in model_list if model['table_name'] != 'N/A']

# ==========================================
# 模型验证函数
# ==========================================

def validate_models():
    """验证模型定义是否正确"""
    issues = []
    model_list = get_all_models()

    for model in model_list:
        model_class = model['class']

        # 检查是否有__tablename__
        if not hasattr(model_class, '__tablename__'):
            issues.append(f"{model['name']}: 缺少 __tablename__ 属性")

        # 检查是否继承自正确的基类
        base_classes = [cls.__name__ for cls in model_class.__mro__]
        if 'BaseEntity' not in base_classes and 'Base' not in base_classes:
            issues.append(f"{model['name']}: Does not inherit BaseEntity or Base")

    if issues:
        # print("\nModel definition issues:")
        # for issue in issues:
        #     print(f"  - {issue}")
        return False
    else:
        # print("\nAll model definitions are correct")
        return True

# ==========================================
# 模型统计信息
# ==========================================

def get_model_statistics():
    """获取模型统计信息"""
    model_list = get_all_models()

    statistics = {
        'total_models': len(model_list),
        'base_models': 0,
        'auth_models': 0,
        'core_models': 0,
        'other_models': 0
    }

    for model in model_list:
        name = model['name']
        if 'Base' in name:
            statistics['base_models'] += 1
        elif name in ['LoginLogEntity', 'UserSocialEntity']:
            statistics['auth_models'] += 1
        elif name in ['UserEntity', 'RoleEntity', 'MenuEntity', 'UserRoleEntity', 'RoleMenuEntity', 'ClientEntity']:
            statistics['core_models'] += 1
        else:
            statistics['other_models'] += 1

    return statistics

if __name__ == "__main__":
    # 直接运行此文件可以查看模型注册情况
    print("Checking database model registration...")

    model_data = print_registered_models()
    validate_models()

    model_stats = get_model_statistics()
    print("\nModel statistics:")
    print(f"  Base models: {model_stats['base_models']}")
    print(f"  Auth modules: {model_stats['auth_models']}")
    print(f"  Core modules: {model_stats['core_models']}")
    print(f"  Other modules: {model_stats['other_models']}")
    print(f"  Total: {model_stats['total_models']}")