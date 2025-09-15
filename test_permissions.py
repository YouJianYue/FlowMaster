# -*- coding: utf-8 -*-

"""
快速测试权限系统的脚本
"""

import asyncio
import json
from datetime import datetime, timedelta
import jwt
from apps.system.core.service.impl.permission_service_impl import PermissionServiceImpl
from apps.common.config.database.database_session import DatabaseSession

# 生成一个测试JWT Token
SECRET_KEY = "test_secret_key_for_flowmaster_permissions"
ALGORITHM = "HS256"

def create_test_token(user_id: int = 1, username: str = "admin") -> str:
    """创建测试JWT令牌"""
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

async def test_permissions():
    """测试权限系统"""
    print("🔍 测试权限系统...")
    
    try:
        # 1. 测试权限服务
        permission_service = PermissionServiceImpl()
        
        print("\n📋 测试用户ID=1的权限查询:")
        permissions = await permission_service.get_user_permissions(1)
        print(f"权限数量: {len(permissions)}")
        if permissions:
            print(f"前10个权限: {list(permissions)[:10]}")
        else:
            print("⚠️ 未找到权限，将使用默认权限")
        
        print("\n👤 测试用户角色查询:")
        roles = await permission_service.get_user_roles(1)
        print(f"角色列表: {roles}")
        
        # 2. 生成测试Token
        test_token = create_test_token()
        print(f"\n🔐 测试Token已生成: {test_token[:50]}...")
        
        # 3. 生成curl测试命令
        print("\n🚀 使用以下命令测试/auth/user/info接口:")
        curl_cmd = f'''curl -X GET "http://localhost:8000/auth/user/info" \\
  -H "Authorization: Bearer {test_token}"'''
        print(curl_cmd)
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_permissions())