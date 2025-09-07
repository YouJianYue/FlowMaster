# -*- coding: utf-8 -*-

"""
验证码控制器
"""

import io
import base64
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse
from PIL import Image, ImageDraw, ImageFont
import random
import uuid as uuid_module
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/captcha", tags=["验证码"])


class CaptchaGenerator:
    """图形验证码生成器"""

    @staticmethod
    def generate_code(length: int = 4) -> str:
        """生成验证码字符串"""
        # 使用数字和大写字母，排除容易混淆的字符
        chars = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'
        return ''.join(random.choices(chars, k=length))

    @staticmethod
    def create_image(code: str, width: int = 120, height: int = 50) -> bytes:
        """创建验证码图片"""
        try:
            # 创建图片
            image = Image.new('RGB', (width, height), color=(255, 255, 255))
            draw = ImageDraw.Draw(image)

            # 尝试使用系统字体，如果失败则使用默认字体
            try:
                font = ImageFont.truetype("Arial.ttf", 28)
            except:
                try:
                    # macOS系统字体
                    font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 28)
                except:
                    # 使用默认字体
                    font = ImageFont.load_default()

            # 绘制背景干扰线
            for _ in range(random.randint(3, 6)):
                x1, y1 = random.randint(0, width), random.randint(0, height)
                x2, y2 = random.randint(0, width), random.randint(0, height)
                draw.line([(x1, y1), (x2, y2)], fill=(200, 200, 200), width=1)

            # 绘制验证码字符
            char_width = width // len(code)
            for i, char in enumerate(code):
                x = char_width * i + random.randint(5, 15)
                y = random.randint(5, 15)
                color = (
                    random.randint(50, 150),
                    random.randint(50, 150),
                    random.randint(50, 150)
                )
                draw.text((x, y), char, font=font, fill=color)

            # 添加噪点
            for _ in range(random.randint(50, 100)):
                x, y = random.randint(0, width - 1), random.randint(0, height - 1)
                draw.point((x, y), fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

            # 转换为字节流
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='PNG')
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
        
        return JSONResponse(content={
            "data": {
                "uuid": captcha_uuid,
                "img": img_data_url,
                "expireTime": expire_timestamp,
                "isEnabled": True
            },
            "timestamp": int(datetime.now().timestamp() * 1000)
        })
        
    except Exception as e:
        logger.error(f"Error generating captcha: {e}")
        raise HTTPException(status_code=500, detail="验证码生成失败")


@router.get("/image", summary="获取图形验证码")
async def get_captcha_image():
    """
    获取图形验证码
    
    参考项目直接返回CaptchaResp对象，不包装在R.ok()中
    
    Returns:
        CaptchaResp格式的验证码信息
    """
    try:
        # 清理过期验证码
        clean_expired_captcha()
        
        # 检查验证码是否启用（这里简化为总是启用）
        # 在参考项目中，这里会检查 optionService.getValueByCode2Int("LOGIN_CAPTCHA_ENABLED")
        # 如果未启用，返回 {"isEnabled": false}
        
        # 生成UUID
        captcha_uuid = str(uuid_module.uuid4())
        
        # 生成验证码
        code = CaptchaGenerator.generate_code(4)
        image_bytes = CaptchaGenerator.create_image(code)
        
        # 转换为base64（带data:image/png;base64前缀）
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

        # 参考项目使用统一的响应格式包装
        return JSONResponse(content={
            "code": "0",
            "msg": "ok", 
            "success": True,
            "timestamp": int(datetime.now().timestamp() * 1000),
            "data": {
                "uuid": captcha_uuid,
                "img": img_data_url,
                "expireTime": expire_timestamp,
                "isEnabled": True
            }
        })

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
        if uuid not in captcha_cache:
            return JSONResponse(
                status_code=400,
                content={"success": False, "code": "400", "msg": "验证码已过期或不存在"}
            )

        cached_data = captcha_cache[uuid]

        # 验证码（忽略大小写）
        if code.lower() != cached_data['code']:
            return JSONResponse(
                status_code=400,
                content={"success": False, "code": "400", "msg": "验证码错误"}
            )

        # 验证成功，删除验证码（一次性使用）
        del captcha_cache[uuid]

        return JSONResponse(
            content={"success": True, "code": "0", "msg": "验证成功"}
        )

    except Exception as e:
        logger.error(f"Error verifying captcha: {e}")
        raise HTTPException(status_code=500, detail="验证码校验失败")


@router.get("/status", summary="获取验证码状态")
async def get_captcha_status():
    """获取验证码缓存状态（开发调试用）"""
    clean_expired_captcha()

    return {
        "active_captchas": len(captcha_cache),
        "captcha_keys": list(captcha_cache.keys()) if logger.level <= logging.DEBUG else "隐藏"
    }
