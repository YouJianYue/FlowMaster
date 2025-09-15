# -*- coding: utf-8 -*-

"""
数据库模型注册模块 - 确保所有模型被SQLAlchemy识别
"""

# 导入数据库基类
from apps.common.config.database.database_config import Base

# ==========================================
# 导入所有实体类，确保它们被SQLAlchemy识别
# ==========================================

# 基础实体类（必须最先导入）
from apps.common.base.model.entity.base_entity import BaseEntity
from apps.common.base.model.entity.base_create_entity import BaseCreateEntity  
from apps.common.base.model.entity.base_update_entity import BaseUpdateEntity
from apps.common.base.model.entity.tenant_base_entity import TenantBaseEntity

# 认证模块实体类
from apps.system.auth.model.entity.login_log_entity import LoginLogEntity
from apps.system.auth.model.entity.user_social_entity import UserSocialEntity

# 系统核心模块实体类
try:
    from apps.system.core.model.entity.user_entity import UserEntity
    from apps.system.core.model.entity.role_entity import RoleEntity
    from apps.system.core.model.entity.menu_entity import MenuEntity
    from apps.system.core.model.entity.dept_entity import DeptEntity
    from apps.system.core.model.entity.user_role_entity import UserRoleEntity
    from apps.system.core.model.entity.role_menu_entity import RoleMenuEntity
    from apps.system.core.model.entity.role_dept_entity import RoleDeptEntity
    from apps.system.core.model.entity.client_entity import ClientEntity
except ImportError as e:
    # 如果某些实体类不存在，跳过（开发阶段可能未完成）
    print(f"Warning: Some entity classes not found: {e}")

# ==========================================
# 收集所有已注册的模型
# ==========================================

def get_all_models():
    """获取所有已注册的数据库模型"""
    models = []
    
    # 通过Base.registry._class_registry获取所有模型
    for mapper in Base.registry.mappers:
        model_class = mapper.class_
        models.append({
            'name': model_class.__name__,
            'table_name': getattr(model_class, '__tablename__', 'N/A'),
            'class': model_class
        })
    
    return models

def print_registered_models():
    """打印所有已注册的模型信息"""
    models = get_all_models()
    
    print("\n📋 已注册的数据库模型:")
    print("-" * 60)
    for i, model in enumerate(models, 1):
        print(f"{i:2d}. {model['name']:<20} -> {model['table_name']}")
    print("-" * 60)
    print(f"总计: {len(models)} 个模型")
    
    return models

def get_table_names():
    """获取所有表名列表"""
    models = get_all_models()
    return [model['table_name'] for model in models if model['table_name'] != 'N/A']

# ==========================================
# 模型验证函数
# ==========================================

def validate_models():
    """验证模型定义是否正确"""
    issues = []
    models = get_all_models()
    
    for model in models:
        model_class = model['class']
        
        # 检查是否有__tablename__
        if not hasattr(model_class, '__tablename__'):
            issues.append(f"{model['name']}: 缺少 __tablename__ 属性")
        
        # 检查是否继承自正确的基类
        base_classes = [cls.__name__ for cls in model_class.__mro__]
        if 'BaseEntity' not in base_classes and 'Base' not in base_classes:
            issues.append(f"{model['name']}: 未继承 BaseEntity 或 Base")
    
    if issues:
        print("\n⚠️  模型定义问题:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("\n✅ 所有模型定义正确")
        return True

# ==========================================
# 模型统计信息
# ==========================================

def get_model_statistics():
    """获取模型统计信息"""
    models = get_all_models()
    
    stats = {
        'total_models': len(models),
        'base_models': 0,
        'auth_models': 0,
        'core_models': 0,
        'other_models': 0
    }
    
    for model in models:
        name = model['name']
        if 'Base' in name:
            stats['base_models'] += 1
        elif name in ['LoginLogEntity', 'UserSocialEntity']:
            stats['auth_models'] += 1
        elif name in ['UserEntity', 'RoleEntity', 'MenuEntity', 'UserRoleEntity', 'RoleMenuEntity', 'ClientEntity']:
            stats['core_models'] += 1
        else:
            stats['other_models'] += 1
    
    return stats

if __name__ == "__main__":
    # 直接运行此文件可以查看模型注册情况
    print("🔍 检查数据库模型注册情况...")
    
    models = print_registered_models()
    validate_models()
    
    stats = get_model_statistics()
    print(f"\n📊 模型统计:")
    print(f"  基础模型: {stats['base_models']} 个")
    print(f"  认证模块: {stats['auth_models']} 个") 
    print(f"  核心模块: {stats['core_models']} 个")
    print(f"  其他模块: {stats['other_models']} 个")
    print(f"  总计: {stats['total_models']} 个")