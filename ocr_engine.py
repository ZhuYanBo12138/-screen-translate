"""
OCR引擎 - 使用Tesseract进行文字识别
"""

import logging
import os
import shutil
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logger.warning("pytesseract 未安装")

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.error("PIL 未安装")


class OCREngine:
    """Tesseract OCR引擎封装"""

    def __init__(self, languages: str = "chi_sim+eng", tesseract_cmd: Optional[str] = None):
        """
        Args:
            languages: OCR语言代码，如 "chi_sim+eng"
            tesseract_cmd: tesseract可执行文件路径（可选）
        """
        self.languages = languages

        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        elif not self._check_tesseract_cmd():
            # 尝试常见路径
            self._find_tesseract()

    def _check_tesseract_cmd(self) -> bool:
        """检查tesseract命令是否已配置"""
        cmd = getattr(pytesseract.pytesseract, 'tesseract_cmd', None)
        if cmd and os.path.exists(cmd):
            return True
        return False

    def _find_tesseract(self):
        """尝试在常见位置找到tesseract"""
        common_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            "/usr/bin/tesseract",
            "/usr/local/bin/tesseract",
        ]

        for path in common_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                logger.info(f"找到Tesseract: {path}")
                return

        # 检查PATH中是否有tesseract
        tesseract_in_path = shutil.which("tesseract")
        if tesseract_in_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_in_path
            logger.info(f"在PATH中找到Tesseract: {tesseract_in_path}")
        else:
            logger.warning("未找到Tesseract，请确保已安装并配置tesseract_cmd路径")

    def recognize(self, image_path: str) -> Optional[str]:
        """
        从图片文件中识别文字

        Args:
            image_path: 图片文件路径

        Returns:
            识别的文字，失败返回None
        """
        if not TESSERACT_AVAILABLE or not PIL_AVAILABLE:
            logger.error("缺少必要依赖: pytesseract 或 PIL")
            return None

        try:
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img, lang=self.languages, timeout=30)
            return text.strip() if text else None
        except Exception as e:
            logger.error(f"OCR识别失败: {e}")
            return None

    def recognize_image(self, image) -> Optional[str]:
        """
        从PIL Image对象识别文字

        Args:
            image: PIL Image对象

        Returns:
            识别的文字，失败返回None
        """
        if not TESSERACT_AVAILABLE or not PIL_AVAILABLE:
            logger.error("缺少必要依赖: pytesseract 或 PIL")
            return None

        try:
            text = pytesseract.image_to_string(image, lang=self.languages, timeout=30)
            return text.strip() if text else None
        except Exception as e:
            logger.error(f"OCR识别失败: {e}")
            return None

    def recognize_image_with_words(self, image):
        """
        从PIL Image对象识别文字，返回每个单词的位置信息

        Args:
            image: PIL Image对象

        Returns:
            (full_text, [(word, x, y, w, h), ...]) 或 (None, [])
        """
        if not TESSERACT_AVAILABLE or not PIL_AVAILABLE:
            logger.error("缺少必要依赖: pytesseract 或 PIL")
            return None, []

        try:
            data = pytesseract.image_to_data(image, lang=self.languages, output_type=pytesseract.Output.DICT)
            words = []
            full_text_lines = []
            n = len(data['text'])

            for i in range(n):
                text = data['text'][i].strip()
                if text:
                    x = data['left'][i]
                    y = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]
                    conf = float(data['conf'][i])
                    if conf > 0:  # 过滤掉置信度为负的无效识别
                        words.append((text, x, y, w, h))
                    full_text_lines.append(text)

            full_text = ' '.join(full_text_lines)
            return full_text, words
        except Exception as e:
            logger.error(f"OCR识别失败: {e}")
            return None, []

    @staticmethod
    def get_tesseract_version() -> Optional[str]:
        """获取Tesseract版本"""
        if not TESSERACT_AVAILABLE:
            return None
        try:
            return pytesseract.get_tesseract_version()
        except Exception:
            return None

    @staticmethod
    def get_available_languages() -> list:
        """获取可用的语言列表"""
        if not TESSERACT_AVAILABLE:
            return []
        try:
            return pytesseract.get_languages()
        except Exception:
            return []


def ocr_image(image_path: str, languages: str = "chi_sim+eng") -> Optional[str]:
    """
    便捷OCR函数

    Args:
        image_path: 图片路径
        languages: 语言代码

    Returns:
        识别的文字
    """
    engine = OCREngine(languages=languages)
    return engine.recognize(image_path)
