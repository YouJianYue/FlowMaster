# -*- coding: utf-8 -*-

"""
验证码控制器
"""

import io
import base64
import logging

from fastapi import APIRouter, HTTPException
from PIL import Image, ImageDraw, ImageFont
import random
import uuid as uuid_module
from datetime import datetime, timedelta

from apps.common.config.captcha_properties import get_captcha_properties
from apps.common.models.api_response import create_success_response
from apps.common.config.logging.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/captcha", tags=["验证码"])

# 获取验证码配置
captcha_properties = get_captcha_properties()


class CaptchaGenerator:
    """图形验证码生成器 - 完全复刻参考项目实现"""

    @staticmethod
    def generate_code(length: int = None) -> str:
        """
        生成验证码字符串

        Args:
            length: 验证码长度，如果为None则使用配置文件的值
        """
        if length is None:
            length = captcha_properties.get_graphic_config().length

        # 使用数字和大写字母，排除容易混淆的字符（与参考项目一致）
        chars = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'
        return ''.join(random.choices(chars, k=length))

    @staticmethod
    def create_image(code: str) -> bytes:
        """
        创建验证码图片 - 一比一复刻参考项目SPEC类型验证码样式

        参考 continew-starter-captcha-graphic 的SPEC类型配置：
        - 类型：SPEC（规范化样式）
        - 尺寸：116x36 (参考项目标准尺寸)
        - 样式：模拟Easy Captcha库的SPEC类型外观
        """
        # 从配置获取图片尺寸
        config = captcha_properties.get_graphic_config()
        width = config.width
        height = config.height

        try:
            # 创建图片 - 使用参考项目的标准尺寸
            image = Image.new('RGB', (width, height), color=(255, 255, 255))
            draw = ImageDraw.Draw(image)

            # SPEC类型验证码特征：更规范的字体和样式
            # 参考Easy Captcha SPEC类型在116x36图片中的字体大小
            font_size = 26  # 调整为更接近SPEC类型的字体大小

            # 跨平台字体查找，优先选择更规范的字体
            font = None
            font_paths = [
                # Windows 系统字体 - 优先选择更规范的字体
                "C:/Windows/Fonts/consola.ttf",      # Consolas - 更规范
                "C:/Windows/Fonts/arial.ttf",        # Arial
                "C:/Windows/Fonts/Arial.ttf",
                "C:/Windows/Fonts/calibri.ttf",
                # macOS 系统字体
                "/System/Library/Fonts/Monaco.ttc",   # Monaco - 等宽字体
                "/System/Library/Fonts/Arial.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
                # Linux 系统字体
                "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",  # 等宽字体
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/TTF/arial.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            ]

            # 尝试加载系统字体
            for font_path in font_paths:
                try:
                    import os
                    if os.path.exists(font_path):
                        font = ImageFont.truetype(font_path, font_size)
                        logger.debug(f"Successfully loaded font: {font_path}")
                        break
                except Exception as e:
                    logger.debug(f"Failed to load font {font_path}: {e}")
                    continue

            # 如果所有字体都加载失败，使用默认字体
            if font is None:
                try:
                    font = ImageFont.truetype("arial", font_size)
                except:
                    try:
                        font = ImageFont.load_default()
                        logger.warning("Using PIL default font - SPEC style may be affected")
                    except:
                        font = ImageFont.load_default()
                        logger.error("Could not load any font - using basic default")

            # SPEC类型特征：简洁的背景干扰 - 减少干扰线，更规范
            for _ in range(random.randint(1, 2)):  # 减少干扰线数量
                x1, y1 = random.randint(0, width), random.randint(0, height)
                x2, y2 = random.randint(0, width), random.randint(0, height)
                # 使用更浅的颜色，不影响可读性
                draw.line([(x1, y1), (x2, y2)], fill=(230, 230, 230), width=1)

            # SPEC类型字符绘制 - 更规范化的布局
            char_width = width // len(code)  # 每个字符的平均宽度

            # SPEC类型特征：使用固定的颜色范围，不太随机
            spec_colors = [
                (30, 30, 30),      # 深灰
                (50, 50, 150),     # 深蓝
                (150, 50, 50),     # 深红
                (50, 150, 50),     # 深绿
                (100, 50, 150),    # 深紫
                (150, 100, 50),    # 深橙
            ]

            for i, char in enumerate(code):
                # SPEC类型布局：更规范的字符位置计算
                x = char_width * i + (char_width - font_size) // 2 + random.randint(-2, 2)
                y = (height - font_size) // 2 + random.randint(-2, 2)

                # 确保字符不会超出图片边界
                x = max(3, min(x, width - font_size - 3))
                y = max(3, min(y, height - font_size - 3))

                # SPEC类型颜色：从预定义颜色中选择
                color = random.choice(spec_colors)

                # 绘制字符 - SPEC类型不使用旋转，保持清晰
                draw.text((x, y), char, font=font, fill=color)

            # SPEC类型噪点：更少更规范的噪点
            for _ in range(random.randint(8, 15)):  # 减少噪点数量
                x, y = random.randint(0, width - 1), random.randint(0, height - 1)
                # 使用更浅的噪点颜色
                noise_color = (random.randint(200, 240), random.randint(200, 240), random.randint(200, 240))
                draw.point((x, y), fill=noise_color)

            # 转换为字节流
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='PNG', quality=95)
            img_buffer.seek(0)

            return img_buffer.getvalue()

        except Exception as e:
            logger.error(f"Failed to create captcha image: {e}")
            raise HTTPException(status_code=500, detail="验证码生成失败")


# 简单的内存缓存（生产环境应使用Redis）
captcha_cache = {}


def clean_expired_captcha():
    """清理过期的验证码"""
    current_time = datetime.now()
    expired_keys = [
        key for key, data in captcha_cache.items()
        if current_time > data['expire_time']
    ]
    for key in expired_keys:
        del captcha_cache[key]


@router.get("/generate", summary="生成验证码信息")
async def generate_captcha():
    """
    生成验证码信息（JSON格式）
    
    Returns:
        验证码信息：uuid、base64图片、过期时间、是否启用
    """
    try:
        # 清理过期验证码
        clean_expired_captcha()

        # 生成UUID
        captcha_uuid = str(uuid_module.uuid4())

        # 生成验证码
        code = CaptchaGenerator.generate_code(4)
        image_bytes = CaptchaGenerator.create_image(code)

        # 转换为base64
        img_base64 = base64.b64encode(image_bytes).decode('utf-8')
        img_data_url = f"data:image/png;base64,{img_base64}"

        # 缓存验证码（5分钟过期）
        expire_time = datetime.now() + timedelta(minutes=5)
        expire_timestamp = int(expire_time.timestamp() * 1000)  # 毫秒时间戳

        captcha_cache[captcha_uuid] = {
            'code': code.lower(),  # 存储小写，验证时忽略大小写
            'expire_time': expire_time
        }

        logger.info(f"Generated captcha for UUID {captcha_uuid}: {code}")

        # 构造CaptchaResp格式的数据
        captcha_data = {
            "uuid": captcha_uuid,
            "img": img_data_url,
            "expireTime": expire_timestamp,
            "isEnabled": True
        }

        # 使用统一响应格式包装
        return create_success_response(data=captcha_data)

    except Exception as e:
        logger.error(f"Error generating captcha: {e}")
        raise HTTPException(status_code=500, detail="验证码生成失败")


@router.get("/image", summary="获取图形验证码")
async def get_captcha_image():
    """
    获取图形验证码

    完全复刻参考项目CaptchaController.getImageCaptcha()方法：
    - 检查验证码是否启用
    - 生成UUID和验证码
    - 设置过期时间
    - 返回CaptchaResp格式

    Returns:
        CaptchaResp格式的验证码信息
    """
    try:
        # 清理过期验证码
        clean_expired_captcha()

        # 检查验证码是否启用（参考项目检查：LOGIN_CAPTCHA_ENABLED）
        # 这里简化为总是启用，实际应该从系统配置中读取
        # login_captcha_enabled = option_service.get_value_by_code_2_int("LOGIN_CAPTCHA_ENABLED")
        # if GlobalConstants.Boolean.NO.equals(login_captcha_enabled):
        #     return CaptchaResp.builder().isEnabled(false).build()

        # 生成UUID（参考项目使用 IdUtil.fastUUID()）
        captcha_uuid = str(uuid_module.uuid4()).replace('-', '')  # 去掉连字符，匹配参考项目格式

        # 生成验证码
        code = CaptchaGenerator.generate_code()
        image_bytes = CaptchaGenerator.create_image(code)

        # 转换为base64（带data:image/png;base64前缀）
        img_base64 = base64.b64encode(image_bytes).decode('utf-8')
        img_data_url = f"data:image/png;base64,{img_base64}"

        # 设置过期时间（从配置读取）
        expire_minutes = captcha_properties.expiration_in_minutes
        expire_time = datetime.now() + timedelta(minutes=expire_minutes)
        expire_timestamp = int(expire_time.timestamp() * 1000)  # 毫秒时间戳

        # 缓存验证码
        captcha_key = f"captcha:{captcha_uuid}"  # 使用参考项目的key格式
        captcha_cache[captcha_key] = {
            'code': code.lower(),  # 存储小写，验证时忽略大小写
            'expire_time': expire_time
        }

        logger.info(f"Generated captcha for UUID {captcha_uuid}: {code}")

        # 构造CaptchaResp格式的数据
        captcha_data = {
            "uuid": captcha_uuid,
            "img": img_data_url,
            "expireTime": expire_timestamp,
            "isEnabled": True
        }

        # 使用统一响应格式包装 (与项目其他接口保持一致)
        return create_success_response(data=captcha_data)

    except Exception as e:
        logger.error(f"Error generating captcha: {e}")
        raise HTTPException(status_code=500, detail="验证码生成失败")


@router.post("/verify", summary="验证图形验证码")
async def verify_captcha(uuid: str, code: str):
    """
    验证图形验证码
    
    Args:
        uuid: 验证码UUID
        code: 用户输入的验证码
        
    Returns:
        验证结果
    """
    try:
        # 清理过期验证码
        clean_expired_captcha()

        # 检查验证码是否存在
        captcha_key = f"captcha:{uuid}"  # 使用正确的缓存键格式
        if captcha_key not in captcha_cache:
            raise HTTPException(
                status_code=400,
                detail="验证码已过期或不存在"
            )

        cached_data = captcha_cache[captcha_key]

        # 验证码（忽略大小写）
        if code.lower() != cached_data['code']:
            raise HTTPException(
                status_code=400,
                detail="验证码错误"
            )

        # 验证成功，删除验证码（一次性使用）
        del captcha_cache[captcha_key]

        return create_success_response(data=True, message="验证成功")

    except Exception as e:
        logger.error(f"Error verifying captcha: {e}")
        raise HTTPException(status_code=500, detail="验证码校验失败")


@router.get("/status", summary="获取验证码状态")
async def get_captcha_status():
    """获取验证码缓存状态（开发调试用）"""
    clean_expired_captcha()

    status_data = {
        "active_captchas": len(captcha_cache),
        "captcha_keys": list(captcha_cache.keys()) if logger.level <= logging.DEBUG else "隐藏"
    }

    return create_success_response(data=status_data)
