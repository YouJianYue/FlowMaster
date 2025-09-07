# -*- coding: utf-8 -*-

"""
测试配置和工具
"""

import pytest
from fastapi.testclient import TestClient
from main import app

# 创建测试客户端
@pytest.fixture
def client():
    """FastAPI测试客户端"""
    return TestClient(app)

@pytest.fixture  
def auth_headers():
    """认证头部fixture"""
    return {}

@pytest.fixture
def sample_login_data():
    """示例登录数据"""
    return {
        "username": "admin",
        "password": "123456"
    }

@pytest.fixture
def invalid_login_data():
    """无效登录数据"""
    return {
        "username": "wrong_user", 
        "password": "wrong_password"
    }