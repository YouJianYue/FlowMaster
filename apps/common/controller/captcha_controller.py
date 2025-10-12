# -*- coding: utf-8 -*-

"""
验证码控制器

一比一复刻参考项目 CaptchaController.java
使用 PIL 模拟 easy-captcha 的 SpecCaptcha 类型验证码
"""

import io
import base64
import random
import uuid as uuid_module
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException
from PIL import Image, ImageDraw, ImageFont

from apps.common.config.captcha_properties import get_captcha_properties
from apps.common.models.api_response import create_success_response
from apps.common.config.logging.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/captcha", tags=["验证码"])

# 获取验证码配置
captcha_properties = get_captcha_properties()


class SpecCaptchaGenerator:
    """
    SPEC类型验证码生成器

    一比一复刻 easy-captcha 的 SpecCaptcha 实现：
    - 参考源码: com.wf.captcha.SpecCaptcha
    - GitHub: https://github.com/ele-admin/EasyCaptcha
    """

    # 常用颜色 - 一比一复刻 easy-captcha 的 COLOR 数组
    COLORS = [
        (0, 135, 255),      # 蓝色
        (51, 153, 51),      # 绿色
        (255, 102, 102),    # 红色
        (255, 153, 0),      # 橙色
        (153, 102, 0),      # 棕色
        (153, 102, 153),    # 紫色
        (51, 153, 153),     # 青色
        (102, 102, 255),    # 浅蓝
        (0, 102, 204),      # 深蓝
        (204, 51, 51),      # 深红
        (0, 153, 204),      # 天蓝
        (0, 51, 102),       # 深蓝绿
    ]

    def __init__(self, width=116, height=36):
        """
        初始化 SPEC 类型验证码生成器

        Args:
            width: 图片宽度，默认116（参考项目标准）
            height: 图片高度，默认36（参考项目标准）
        """
        self.width = width
        self.height = height
        self.font = self._load_font()

    def _load_font(self):
        """加载字体 - 一比一复刻 easy-captcha 的字体加载逻辑"""
        # 参考项目默认字体大小适配高度
        font_size = 32

        # 尝试加载系统字体（优先 Arial Bold）
        font_paths = [
            # Windows
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/arial.ttf",
            # macOS
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            # Linux
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]

        for font_path in font_paths:
            try:
                import os
                if os.path.exists(font_path):
                    return ImageFont.truetype(font_path, font_size)
            except:
                continue

        # 如果都失败，使用默认字体
        try:
            return ImageFont.truetype("arial", font_size)
        except:
            return ImageFont.load_default()

    def _random_color(self):
        """随机颜色 - 一比一复刻 color() 方法"""
        return random.choice(self.COLORS)

    def _draw_oval(self, num, draw):
        """
        画干扰圆 - 一比一复刻 drawOval() 方法

        Args:
            num: 数量
            draw: ImageDraw对象
        """
        for i in range(num):
            color = self._random_color()
            # w = 5 + num(10) => 5到15之间
            w = 5 + random.randint(0, 10)
            # drawOval(num(width-25), num(height-15), w, w)
            x = random.randint(0, self.width - 25)
            y = random.randint(0, self.height - 15)
            draw.ellipse([x, y, x + w, y + w], outline=color)

    def _draw_bezier_line(self, num, draw):
        """
        画贝塞尔曲线 - 一比一复刻 drawBesselLine() 方法

        参考实现：
        int x1 = 5, y1 = num(5, height / 2);
        int x2 = width - 5, y2 = num(height / 2, height - 5);
        int ctrlx = num(width / 4, width / 4 * 3)
        int ctrly = num(5, height - 5);

        Args:
            num: 数量
            draw: ImageDraw对象
        """
        from PIL import ImageDraw

        for i in range(num):
            color = self._random_color()

            # 起点和终点
            x1, y1 = 5, random.randint(5, self.height // 2)
            x2, y2 = self.width - 5, random.randint(self.height // 2, self.height - 5)

            # 控制点
            ctrlx = random.randint(self.width // 4, self.width // 4 * 3)
            ctrly = random.randint(5, self.height - 5)

            # 随机交换y1和y2
            if random.randint(0, 1) == 0:
                y1, y2 = y2, y1

            # 绘制二阶贝塞尔曲线（简化实现）
            # 使用多段直线近似贝塞尔曲线
            points = []
            for t in range(0, 101, 5):
                t = t / 100.0
                # 二阶贝塞尔曲线公式: B(t) = (1-t)²P0 + 2(1-t)tP1 + t²P2
                x = int((1-t)**2 * x1 + 2*(1-t)*t*ctrlx + t**2 * x2)
                y = int((1-t)**2 * y1 + 2*(1-t)*t*ctrly + t**2 * y2)
                points.append((x, y))

            # 画曲线（线宽2f）
            draw.line(points, fill=color, width=2)

    def generate(self, code):
        """
        生成验证码图片 - 一比一复刻 graphicsImage() 方法

        参考实现流程：
        1. 创建 BufferedImage
        2. 填充白色背景
        3. 开启抗锯齿
        4. 画干扰圆 drawOval(2, g2d)
        5. 设置线宽2f，画贝塞尔线 drawBesselLine(1, g2d)
        6. 画字符串（均匀分布）

        Args:
            code: 验证码文本

        Returns:
            BytesIO 对象
        """
        # 创建图片 - BufferedImage.TYPE_INT_RGB
        image = Image.new('RGB', (self.width, self.height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)

        # 抗锯齿 - 等同于 g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, ...)
        # PIL的ImageDraw在绘制文字时默认开启抗锯齿

        # 画干扰圆 - drawOval(2, g2d)
        self._draw_oval(2, draw)

        # 画干扰线 - drawBesselLine(1, g2d)
        self._draw_bezier_line(1, draw)

        # 画字符串
        # int fW = width / strs.length;
        fW = self.width // len(code)

        for i, char in enumerate(code):
            # 随机颜色
            color = self._random_color()

            # 计算字符位置 - 一比一复刻参考项目的布局算法
            # FontMetrics fontMetrics = g2d.getFontMetrics();
            # int fSp = (fW - (int) fontMetrics.getStringBounds("W", g2d).getWidth()) / 2;
            # g2d.drawString(String.valueOf(strs[i]), i * fW + fSp + 3, fY - 3);

            try:
                bbox = draw.textbbox((0, 0), char, font=self.font)
                char_width = bbox[2] - bbox[0]
                char_height = bbox[3] - bbox[1]
            except:
                # 兼容旧版PIL
                char_width = 20
                char_height = 28

            # 字符左右边距
            fSp = (fW - char_width) // 2

            # 文字纵坐标 - fY = height - ((height - char_height) >> 1)
            fY = self.height - ((self.height - char_height) >> 1)

            # 绘制字符 - i * fW + fSp + 3, fY - 3
            x = i * fW + fSp + 3
            y = fY - 3 - char_height  # PIL的text坐标是左上角

            draw.text((x, y), char, font=self.font, fill=color)

        # 转换为字节流 - ImageIO.write(bi, "png", out)
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        return img_buffer


class CaptchaGenerator:
    """图形验证码生成器 - 一比一复刻参考项目实现"""

    # SPEC类型验证码生成器实例
    _spec_captcha = None

    @classmethod
    def get_captcha_instance(cls):
        """获取验证码生成器实例（单例模式）"""
        if cls._spec_captcha is None:
            config = captcha_properties.get_graphic_config()
            cls._spec_captcha = SpecCaptchaGenerator(
                width=config.width,
                height=config.height
            )
        return cls._spec_captcha

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

    @classmethod
    def create_image(cls, code: str) -> bytes:
        """
        创建验证码图片

        一比一复刻参考项目：
        Captcha captcha = graphicCaptchaService.getCaptcha();
        captcha.toBase64();

        Args:
            code: 验证码文本

        Returns:
            PNG格式的图片字节
        """
        try:
            # 获取 SPEC 类型验证码生成器
            captcha_gen = cls.get_captcha_instance()

            # 生成验证码图片
            image_data = captcha_gen.generate(code)

            # 读取字节数据
            return image_data.read()

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
