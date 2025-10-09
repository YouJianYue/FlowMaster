# -*- coding: utf-8 -*-

"""
JWT 认证配置
"""

import os
import warnings
from typing import Optional
from datetime import datetime, timedelta, UTC
from jose import JWTError, jwt, ExpiredSignatureError
# 抑制 passlib 和 bcrypt 相关警告
with warnings.catch_warnings():
    warnings.simplefilter("ignore", DeprecationWarning)
    warnings.simplefilter("ignore", UserWarning)
    # 专门抑制 bcrypt 版本相关警告
    warnings.filterwarnings("ignore", message=".*bcrypt.*", category=Warning)
    from passlib.context import CryptContext
from pydantic_settings import BaseSettings, SettingsConfigDict


class TokenExpiredException(Exception):
    """Token过期异常"""
    pass


class TokenInvalidException(Exception):
    """Token无效异常"""
    pass


class JWTConfig(BaseSettings):
    """JWT 配置类"""
    
    # JWT 密钥
    secret_key: str = os.getenv("JWT_SECRET_KEY", "flowmaster-jwt-secret-key-change-in-production")
    
    # JWT 算法
    algorithm: str = "HS256"
    
    # 访问令牌过期时间 (分钟)
    access_token_expire_minutes: int = 60 * 24  # 24小时
    
    # 刷新令牌过期时间 (天)
    refresh_token_expire_days: int = 7  # 7天
    
    # 令牌类型
    token_type: str = "bearer"
    
    model_config = SettingsConfigDict(env_prefix="JWT_", extra="ignore")


class PasswordConfig:
    """密码加密配置"""

    # 密码上下文
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """
        验证密码

        支持Spring Security格式的bcrypt密码：{bcrypt}$2a$10$...
        也支持标准bcrypt格式：$2a$10$...
        """
        # 处理Spring Security格式的bcrypt密码 (带{bcrypt}前缀)
        if hashed_password.startswith("{bcrypt}"):
            # 移除{bcrypt}前缀，保留真实的bcrypt哈希
            actual_hash = hashed_password[8:]  # 移除"{bcrypt}"前缀
            return cls.pwd_context.verify(plain_password, actual_hash)
        else:
            # 标准bcrypt格式
            return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        """获取密码哈希"""
        return cls.pwd_context.hash(password)


class JWTUtils:
    """JWT 工具类"""
    
    def __init__(self, config: JWTConfig = None):
        self.config = config or JWTConfig()
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(minutes=self.config.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.config.secret_key, algorithm=self.config.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建刷新令牌"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(days=self.config.refresh_token_expire_days)
        
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.config.secret_key, algorithm=self.config.algorithm)
        return encoded_jwt
    
    def decode_token(self, token: str) -> Optional[dict]:
        """解码令牌"""
        try:
            payload = jwt.decode(token, self.config.secret_key, algorithms=[self.config.algorithm])
            return payload
        except JWTError:
            return None
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[dict]:
        """
        验证令牌

        Args:
            token: JWT令牌
            token_type: 令牌类型（access/refresh）

        Returns:
            dict: JWT payload

        Raises:
            TokenExpiredException: 令牌已过期
            TokenInvalidException: 令牌无效
        """
        try:
            payload = jwt.decode(token, self.config.secret_key, algorithms=[self.config.algorithm])
        except ExpiredSignatureError:
            # Token过期
            raise TokenExpiredException("令牌已过期")
        except JWTError as e:
            # Token无效（格式错误、签名错误等）
            raise TokenInvalidException(f"令牌无效: {str(e)}")

        # 验证令牌类型
        if payload.get("type") != token_type:
            raise TokenInvalidException(f"令牌类型错误，期望 {token_type}，实际 {payload.get('type')}")

        return payload

    def get_current_timestamp(self) -> int:
        """
        获取当前时间戳（毫秒）

        Returns:
            int: 当前时间戳（毫秒）
        """
        return int(datetime.now().timestamp() * 1000)


# 全局实例
jwt_config = JWTConfig()
jwt_utils = JWTUtils(jwt_config)
password_config = PasswordConfig()