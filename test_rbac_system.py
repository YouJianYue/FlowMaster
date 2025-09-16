#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试RBAC权限体系实现

@author: FlowMaster
@since: 2025/9/16
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from apps.system.core.service.role_service import get_role_service
from apps.common.config.database.database_session import DatabaseSession


async def test_rbac_implementation():
    """测试RBAC权限体系实现"""
    print("🧪 测试RBAC权限体系实现...")

    try:
        # 测试角色服务获取
        print("\n1. 测试角色服务初始化...")
        role_service = get_role_service()
        print(f"✅ 角色服务初始化成功: {type(role_service).__name__}")

        # 测试数据库连接
        print("\n2. 测试数据库连接...")
        async with DatabaseSession.get_session_context() as session:
            print("✅ 数据库连接成功")

        # 测试用户权限查询
        print("\n3. 测试用户权限查询...")
        test_user_id = 1  # 假设超级管理员ID为1

        try:
            permissions = await role_service.list_permissions_by_user_id(test_user_id)
            print(f"✅ 用户权限查询成功，权限数量: {len(permissions)}")
            if permissions:
                print(f"   前5个权限: {list(permissions)[:5]}")
            else:
                print("   ⚠️ 权限列表为空")
        except Exception as e:
            print(f"❌ 用户权限查询失败: {str(e)}")

        # 测试用户角色查询
        print("\n4. 测试用户角色查询...")
        try:
            role_codes = await role_service.get_role_codes_by_user_id(test_user_id)
            print(f"✅ 用户角色查询成功，角色数量: {len(role_codes)}")
            if role_codes:
                print(f"   用户角色: {list(role_codes)}")
            else:
                print("   ⚠️ 角色列表为空")
        except Exception as e:
            print(f"❌ 用户角色查询失败: {str(e)}")

        # 测试超级管理员检查
        print("\n5. 测试超级管理员检查...")
        try:
            is_super_admin = await role_service.is_super_admin_user(test_user_id)
            print(f"✅ 超级管理员检查成功: {'是' if is_super_admin else '不是'}")
        except Exception as e:
            print(f"❌ 超级管理员检查失败: {str(e)}")

    except Exception as e:
        print(f"❌ RBAC测试过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_auth_service_route():
    """测试认证服务的路由构建功能"""
    print("\n🚀 测试认证服务路由构建...")

    try:
        from apps.system.auth.service.auth_service_manager import get_auth_service

        # 获取认证服务
        auth_service = get_auth_service()
        print("✅ 认证服务获取成功")

        # 测试路由树构建
        test_user_id = 1
        try:
            routes = await auth_service.build_user_route_tree(test_user_id)
            print(f"✅ 用户路由树构建成功，路由数量: {len(routes)}")

            if routes:
                print("   路由结构:")
                for route in routes:
                    print(f"     - {route['path']}: {route['meta']['title']}")
                    if 'children' in route:
                        for child in route['children']:
                            print(f"       └─ {child['path']}: {child['meta']['title']}")
            else:
                print("   ⚠️ 路由列表为空")

        except Exception as e:
            print(f"❌ 路由树构建失败: {str(e)}")
            import traceback
            traceback.print_exc()

    except Exception as e:
        print(f"❌ 认证服务测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """主测试函数"""
    print("🔥 开始RBAC权限体系功能测试\n")

    # 测试核心RBAC组件
    await test_rbac_implementation()

    # 测试认证服务路由
    await test_auth_service_route()

    print("\n🎉 RBAC权限体系功能测试完成!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试执行失败: {str(e)}")
        import traceback
        traceback.print_exc()