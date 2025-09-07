# -*- coding: utf-8 -*-

"""
JWT工具类测试
"""

import pytest
from datetime import datetime, timedelta
from apps.system.auth.config.jwt_config import JWTUtils, PasswordConfig


class TestJWTUtils:
    """JWT工具类测试"""
    
    def setup_method(self):
        """测试前设置"""
        self.jwt_utils = JWTUtils()
        self.test_data = {"user_id": 1, "username": "test_user"}
    
    def test_create_access_token(self):
        """测试创建访问令牌"""
        token = self.jwt_utils.create_access_token(self.test_data)
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_refresh_token(self):
        """测试创建刷新令牌"""
        token = self.jwt_utils.create_refresh_token(self.test_data)
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_decode_token(self):
        """测试解码令牌"""
        token = self.jwt_utils.create_access_token(self.test_data)
        payload = self.jwt_utils.decode_token(token)
        
        assert payload is not None
        assert payload["user_id"] == self.test_data["user_id"]
        assert payload["username"] == self.test_data["username"]
        assert payload["type"] == "access"
    
    def test_verify_access_token(self):
        """测试验证访问令牌"""
        token = self.jwt_utils.create_access_token(self.test_data)
        payload = self.jwt_utils.verify_token(token, "access")
        
        assert payload is not None
        assert payload["user_id"] == self.test_data["user_id"]
        assert payload["type"] == "access"
    
    def test_verify_refresh_token(self):
        """测试验证刷新令牌"""
        token = self.jwt_utils.create_refresh_token(self.test_data)
        payload = self.jwt_utils.verify_token(token, "refresh")
        
        assert payload is not None
        assert payload["user_id"] == self.test_data["user_id"]
        assert payload["type"] == "refresh"
    
    def test_invalid_token(self):
        """测试无效令牌"""
        invalid_token = "invalid.token.here"
        payload = self.jwt_utils.decode_token(invalid_token)
        assert payload is None
    
    def test_wrong_token_type(self):
        """测试错误令牌类型"""
        access_token = self.jwt_utils.create_access_token(self.test_data)
        # 用access token验证refresh token
        payload = self.jwt_utils.verify_token(access_token, "refresh")
        assert payload is None
    
    def test_expired_token(self):
        """测试过期令牌"""
        # 创建一个立即过期的令牌
        expired_delta = timedelta(seconds=-1)
        token = self.jwt_utils.create_access_token(self.test_data, expired_delta)
        payload = self.jwt_utils.verify_token(token, "access")
        assert payload is None


class TestPasswordConfig:
    """密码配置测试"""
    
    def test_password_hashing(self):
        """测试密码哈希"""
        password = "test_password_123"
        hashed = PasswordConfig.get_password_hash(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0
    
    def test_password_verification_success(self):
        """测试密码验证成功"""
        password = "test_password_123"
        hashed = PasswordConfig.get_password_hash(password)
        
        is_valid = PasswordConfig.verify_password(password, hashed)
        assert is_valid is True
    
    def test_password_verification_failure(self):
        """测试密码验证失败"""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = PasswordConfig.get_password_hash(password)
        
        is_valid = PasswordConfig.verify_password(wrong_password, hashed)
        assert is_valid is False
    
    def test_same_password_different_hashes(self):
        """测试同一密码生成不同哈希"""
        password = "same_password"
        hash1 = PasswordConfig.get_password_hash(password)
        hash2 = PasswordConfig.get_password_hash(password)
        
        # 哈希值应该不同（因为使用了salt）
        assert hash1 != hash2
        
        # 但都应该能验证通过
        assert PasswordConfig.verify_password(password, hash1) is True
        assert PasswordConfig.verify_password(password, hash2) is True