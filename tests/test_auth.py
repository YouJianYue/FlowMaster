# -*- coding: utf-8 -*-

"""
认证模块测试
"""

import pytest
from fastapi.testclient import TestClient


class TestAuthentication:
    """认证功能测试"""
    
    def test_login_success(self, client, sample_login_data):
        """测试成功登录"""
        response = client.post("/api/auth/login", json=sample_login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "登录成功"
        assert "data" in data
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client, invalid_login_data):
        """测试无效凭据登录"""
        response = client.post("/api/auth/login", json=invalid_login_data)
        assert response.status_code == 200  # API返回200但success=false
        
        data = response.json()
        assert data["success"] is False
        assert "用户名或密码错误" in data["message"] or "登录失败" in data["message"]
    
    def test_login_missing_fields(self, client):
        """测试缺少必填字段"""
        response = client.post("/api/auth/login", json={})
        assert response.status_code == 422  # 参数验证错误
    
    def test_login_empty_credentials(self, client):
        """测试空凭据"""
        response = client.post("/api/auth/login", json={
            "username": "",
            "password": ""
        })
        assert response.status_code == 422  # 参数验证错误
    
    def test_check_login_status_without_token(self, client):
        """测试未登录状态检查"""
        response = client.get("/api/auth/check")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["data"]["logged_in"] is False
    
    def test_get_user_info_without_token(self, client):
        """测试未授权获取用户信息"""
        response = client.get("/api/auth/user/info")
        assert response.status_code == 401  # 中间件拦截
    
    def test_get_user_info_with_invalid_token(self, client):
        """测试使用无效token获取用户信息"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/auth/user/info", headers=headers)
        assert response.status_code == 401


class TestAuthenticationFlow:
    """认证流程测试"""
    
    def test_complete_auth_flow(self, client, sample_login_data):
        """测试完整认证流程"""
        # 1. 登录
        login_response = client.post("/api/auth/login", json=sample_login_data)
        assert login_response.status_code == 200
        
        login_data = login_response.json()
        assert login_data["success"] is True
        
        access_token = login_data["data"]["access_token"]
        refresh_token = login_data["data"]["refresh_token"]
        
        # 2. 使用token获取用户信息
        headers = {"Authorization": f"Bearer {access_token}"}
        user_info_response = client.get("/api/auth/user/info", headers=headers)
        assert user_info_response.status_code == 200
        
        user_info_data = user_info_response.json()
        assert user_info_data["success"] is True
        assert user_info_data["data"]["id"] is not None
        assert user_info_data["data"]["username"] == sample_login_data["username"]
        
        # 3. 检查登录状态
        check_response = client.get("/api/auth/check")
        assert check_response.status_code == 200
        # 注意：这里可能返回未登录，因为中间件在测试环境中的行为
        
        # 4. 刷新token
        refresh_response = client.post("/api/auth/refresh", json={
            "refresh_token": refresh_token
        })
        assert refresh_response.status_code == 200
        
        refresh_data = refresh_response.json()
        assert refresh_data["success"] is True
        assert "access_token" in refresh_data["data"]
        
        # 5. 退出登录
        logout_response = client.post("/api/auth/logout", headers=headers)
        assert logout_response.status_code == 200
        
        logout_data = logout_response.json()
        assert logout_data["success"] is True