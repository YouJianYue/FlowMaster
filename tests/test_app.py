# -*- coding: utf-8 -*-

"""
基础应用测试
"""

import pytest


class TestApp:
    """应用基础功能测试"""
    
    def test_health_check(self, client):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "FlowMaster is running" in data["message"]
    
    def test_root_endpoint(self, client):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "Welcome to FlowMaster API" in data["message"]
    
    def test_openapi_docs(self, client):
        """测试API文档端点"""
        response = client.get("/docs")
        assert response.status_code == 200
        
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert "openapi" in response.json()