# -*- coding: utf-8 -*-

"""
CRUD API 权限前缀缓存
"""

from typing import Dict, Type, List


class CrudApiPermissionPrefixCache:
    """CRUD API 权限前缀缓存"""
    
    _PERMISSION_PREFIX_CACHE: Dict[Type, str] = {}
    
    @classmethod
    def put(cls, controller_class: Type, path: str) -> None:
        """
        存储CRUD API权限前缀
        
        Args:
            controller_class: 控制器类
            path: 路径
        """
        permission_prefix = cls._parse_permission_prefix(path)
        cls._PERMISSION_PREFIX_CACHE[controller_class] = permission_prefix
    
    @classmethod
    def get(cls, controller_class: Type) -> str:
        """
        获取CRUD API权限前缀
        
        Args:
            controller_class: 控制器类
            
        Returns:
            权限前缀
        """
        return cls._PERMISSION_PREFIX_CACHE.get(controller_class, "")
    
    @classmethod
    def clear(cls) -> None:
        """清空缓存"""
        cls._PERMISSION_PREFIX_CACHE.clear()
    
    @classmethod
    def get_all(cls) -> Dict[Type, str]:
        """
        获取所有缓存
        
        Returns:
            所有缓存
        """
        return cls._PERMISSION_PREFIX_CACHE.copy()
    
    @classmethod
    def _parse_permission_prefix(cls, path: str) -> str:
        """
        解析权限前缀（解析路径获取模块名和资源名）
        
        例如：/system/user => system:user
             /system/dict/item => system:dictItem
        
        Args:
            path: 路径
            
        Returns:
            权限前缀
            
        Raises:
            ValueError: 无效的路径配置
        """
        # 移除开头的斜杠并分割路径
        path = path.lstrip('/')
        path_segments: List[str] = [segment.strip() for segment in path.split('/') if segment.strip()]
        
        if len(path_segments) < 2:
            raise ValueError(f"无效的 CRUD API 路径配置：/{path}")
        
        module_name = path_segments[0]
        
        # 处理资源名：将多个路径段用下划线连接，然后转为驼峰命名
        resource_segments = path_segments[1:]
        resource_name = cls._to_camel_case('_'.join(resource_segments))
        
        return f"{module_name}:{resource_name}"
    
    @staticmethod
    def _to_camel_case(snake_str: str) -> str:
        """
        将下划线命名转为驼峰命名
        
        Args:
            snake_str: 下划线命名的字符串
            
        Returns:
            驼峰命名的字符串
        """
        if not snake_str:
            return ""
        
        # 分割并处理每个单词
        components = snake_str.split('_')
        if not components:
            return ""
        
        # 第一个单词保持小写，后续单词首字母大写
        result = components[0].lower()
        for component in components[1:]:
            if component:
                result += component.capitalize()
        
        return result