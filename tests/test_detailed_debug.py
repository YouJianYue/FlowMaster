# -*- coding: utf-8 -*-

"""
更详细的调试测试
"""

import pytest
import json
import traceback


class TestDetailedDebug:
    """详细调试测试"""
    
    def test_debug_login_with_logging(self, client, sample_login_data):
        """带日志的登录调试"""
        print(f"\n=== 详细登录调试 ===")
        
        try:
            # 先测试应用是否启动
            health_response = client.get("/health")
            print(f"健康检查: {health_response.status_code} - {health_response.json()}")
            
            # 测试登录
            print(f"登录数据: {sample_login_data}")
            response = client.post("/api/auth/login", json=sample_login_data)
            print(f"登录响应状态: {response.status_code}")
            print(f"登录响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
            
        except Exception as e:
            print(f"测试异常: {e}")
            print(f"异常详情: {traceback.format_exc()}")
        
        assert True
    
    def test_manual_password_check(self):
        """手动测试密码验证"""
        print(f"\n=== 密码验证测试 ===")
        
        try:
            from apps.system.auth.config.jwt_config import password_config
            
            # 测试密码哈希
            password = "123456"
            hashed = password_config.get_password_hash(password)
            print(f"原密码: {password}")
            print(f"哈希后: {hashed}")
            
            # 测试验证
            is_valid = password_config.verify_password(password, hashed)
            print(f"验证结果: {is_valid}")
            
            # 测试模拟用户数据的密码哈希
            mock_hash = password_config.get_password_hash("123456")
            print(f"模拟用户密码哈希: {mock_hash}")
            
        except Exception as e:
            print(f"密码测试异常: {e}")
            print(f"异常详情: {traceback.format_exc()}")
        
        assert True
    
    def test_user_context_debug(self):
        """用户上下文调试"""
        print(f"\n=== 用户上下文调试 ===")
        
        try:
            from apps.common.context.user_context_holder import UserContextHolder
            from apps.common.context.user_context import UserContext
            
            # 测试创建用户上下文
            user_context = UserContext(
                id=1,
                username="admin",
                nickname="管理员",
                email="admin@example.com",
                phone="13888888888",
                avatar=None,
                dept_id=1,
                tenant_id=1,
                client_type="web",
                client_id="web",
                permissions=set(),
                role_codes=set(),
                roles=[]
            )
            
            print(f"用户上下文创建成功: {user_context}")
            
            # 测试设置上下文
            UserContextHolder.set_context(user_context)
            print("用户上下文设置成功")
            
            # 测试获取上下文
            current_context = UserContextHolder.get_context()
            print(f"获取的上下文: {current_context}")
            
        except Exception as e:
            print(f"用户上下文测试异常: {e}")
            print(f"异常详情: {traceback.format_exc()}")
        
        assert True