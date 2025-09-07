# -*- coding: utf-8 -*-

"""
加密/解密工具类
"""

import base64
import re
import binascii
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

from apps.common.config.rsa_properties import RsaProperties
from apps.common.constant import regex_constants


class SecureUtils:
    """加密/解密工具类"""

    def __init__(self):
        # 私有构造函数，防止实例化
        raise RuntimeError("SecureUtils cannot be instantiated")

    @staticmethod
    def encrypt_by_rsa_public_key(data: str) -> str:
        """
        公钥加密
        
        Args:
            data: 要加密的内容
            
        Returns:
            加密后的内容（Base64编码）
        """
        public_key = RsaProperties.PUBLIC_KEY
        if not public_key:
            raise ValueError("请配置 RSA 公钥")
        return SecureUtils.encrypt_by_rsa_public_key_with_key(data, public_key)

    @staticmethod
    def decrypt_by_rsa_private_key(data: str) -> str:
        """
        私钥解密
        
        Args:
            data: 要解密的内容（Base64 加密过）
            
        Returns:
            解密后的内容
        """
        private_key = RsaProperties.PRIVATE_KEY
        if not private_key:
            raise ValueError("请配置 RSA 私钥")
        return SecureUtils.decrypt_by_rsa_private_key_with_key(data, private_key)

    @staticmethod
    def encrypt_by_rsa_public_key_with_key(data: str, public_key_str: str) -> str:
        """
        公钥加密
        
        Args:
            data: 要加密的内容
            public_key_str: 公钥字符串（可以是PEM格式或base64格式）
            
        Returns:
            加密后的内容（Base64编码）
        """
        try:
            # 如果是base64格式的公钥，转换为PEM格式
            if not public_key_str.startswith('-----BEGIN'):
                pem_public_key = f"-----BEGIN PUBLIC KEY-----\n{public_key_str}\n-----END PUBLIC KEY-----"
            else:
                pem_public_key = public_key_str
                
            # 解析公钥
            public_key = serialization.load_pem_public_key(pem_public_key.encode())

            # 加密数据 (使用PKCS1v15 padding，与JSEncrypt前端兼容)
            encrypted = public_key.encrypt(
                data.encode(),
                padding.PKCS1v15()
            )

            # 返回Base64编码的结果
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            raise ValueError(f"RSA公钥加密失败: {str(e)}")

    @staticmethod
    def decrypt_by_rsa_private_key_with_key(data: str, private_key_str: str) -> str:
        """
        私钥解密
        
        Args:
            data: 要解密的内容（Base64 加密过）
            private_key_str: 私钥字符串（可以是PEM格式或base64格式）
            
        Returns:
            解密后的内容
        """
        try:
            # 如果是base64格式的私钥，转换为PEM格式
            if not private_key_str.startswith('-----BEGIN'):
                pem_private_key = f"-----BEGIN PRIVATE KEY-----\n{private_key_str}\n-----END PRIVATE KEY-----"
            else:
                pem_private_key = private_key_str
                
            # 解析私钥
            private_key = serialization.load_pem_private_key(
                pem_private_key.encode(),
                password=None
            )

            # Base64解码
            encrypted_data = base64.b64decode(data.encode())

            # 解密数据 (使用PKCS1v15 padding，与JSEncrypt前端兼容)
            decrypted = private_key.decrypt(
                encrypted_data,
                padding.PKCS1v15()
            )

            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"RSA私钥解密失败: {str(e)}")

    @staticmethod
    def decrypt_password_by_rsa_private_key(encrypted_password: str, error_msg: str) -> str:
        """
        解密密码
        
        Args:
            encrypted_password: 密码（已被 Rsa 公钥加密）
            error_msg: 错误信息
            
        Returns:
            解密后的密码
        """
        return SecureUtils.decrypt_password_by_rsa_private_key_with_pattern(
            encrypted_password, error_msg, False
        )

    @staticmethod
    def decrypt_password_by_rsa_private_key_with_pattern(
            encrypted_password: str,
            error_msg: str,
            is_verify_pattern: bool
    ) -> str:
        """
        解密密码
        
        Args:
            encrypted_password: 密码（已被 Rsa 公钥加密）
            error_msg: 错误信息
            is_verify_pattern: 是否验证密码格式
            
        Returns:
            解密后的密码
        """
        try:
            raw_password = SecureUtils.decrypt_by_rsa_private_key(encrypted_password)
        except (ValueError, TypeError, binascii.Error):
            raw_password = None

        if not raw_password:
            raise ValueError(error_msg)

        if is_verify_pattern:
            # 密码格式验证：8-32个字符，至少包含字母和数字
            if not re.match(regex_constants.PASSWORD, raw_password):
                raise ValueError("密码长度为 8-32 个字符，支持大小写字母、数字、特殊字符，至少包含字母和数字")

        return raw_password
