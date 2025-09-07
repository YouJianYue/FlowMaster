# -*- coding: utf-8 -*-

"""
调试登录问题
"""

import pytest
import json


class TestDebugLogin:
    """调试登录问题"""
    
    def test_debug_login_response(self, client, sample_login_data):
        """调试登录响应内容"""
        response = client.post("/api/auth/login", json=sample_login_data)
        
        print(f"\n=== 登录测试调试信息 ===")
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        # 不做断言，只查看响应内容
        assert True
    
    def test_debug_check_status_response(self, client):
        """调试检查状态响应"""
        response = client.get("/api/auth/check")
        
        print(f"\n=== 检查状态测试调试信息 ===")
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        # 不做断言，只查看响应内容
        assert True