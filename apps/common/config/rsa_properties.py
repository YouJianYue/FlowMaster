# -*- coding: utf-8 -*-

"""
RSA 配置属性
"""

import os


class RsaProperties:
    """RSA 配置属性类"""
    
    # 静态字段，在模块加载时初始化
    PRIVATE_KEY: str = os.getenv("FLOWMASTER_SECURITY_CRYPTO_PRIVATE_KEY", "")
    PUBLIC_KEY: str = os.getenv("FLOWMASTER_SECURITY_CRYPTO_PUBLIC_KEY", "")
    
    def __init__(self):
        # 私有构造函数，防止实例化
        raise RuntimeError("RsaProperties cannot be instantiated")
