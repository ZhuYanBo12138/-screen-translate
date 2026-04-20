"""
屏幕翻译工具 - 主程序
支持快捷键触发截图、OCR识别、在线翻译
"""

import logging
import sys
import os
import threading
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 导入配置
try:
    import config
except ImportError:
    logger.error("配置文件 config.py 不存在")
    sys.exit(1)

# 导入模块
from capture import ScreenCapture, RegionSelector, save_temp_image
from ocr_engine import OCREngine
from translator import Translator
from ui import DesktopOverlay, WordOverlay


class ScreenTranslator:
    """屏幕翻译器主类"""

    def __init__(self):
        self.capture = ScreenCapture()
        self.ocr = OCREngine(languages=config.OCR_LANGUAGES)
        self.translator = Translator(
            provider=config.TRANSLATOR_PROVIDER,
            target_lang=config.TARGET_LANGUAGE,
            api_key=config.DEEPL_API_KEY
        )
        self.running = False

    def capture_and_translate(self):
        """执行截图->OCR->翻译->显示结果"""
        try:
            # 1. 全屏截图
            logger.info("截取全屏...")
            full_img = self.capture.capture_fullscreen()
            if full_img is None:
                logger.error("截图失败")
                return

            # 2. 使用全屏
            x, y, w, h = 0, 0, full_img.width, full_img.height
            logger.info(f"使用全屏: ({x}, {y}, {w}, {h})")

            # 3. 裁剪（这里实际就是全屏）
            cropped_img = full_img.crop((x, y, x + w, y + h))

            # 4. OCR识别（带单词位置）
            logger.info("正在进行OCR识别...")
            original_text, word_list = self.ocr.recognize_image_with_words(cropped_img)

            if not original_text or not word_list:
                logger.warning("未识别到文字")
                self._show_result("未识别到文字", "请确保截图区域包含文字", cropped_img, x, y, w, h)
                return

            logger.info(f"识别到 {len(word_list)} 个单词")

            # 5. 逐词翻译
            logger.info("正在进行翻译...")
            word_translations = []
            for word, wx, wy, ww, wh in word_list:
                translated = self.translator.translate(word)
                if translated:
                    word_translations.append((word, translated, wx, wy, ww, wh))
                else:
                    word_translations.append((word, word, wx, wy, ww, wh))

            logger.info(f"翻译完成，共 {len(word_translations)} 个词")

            # 6. 显示结果（每个单词一个悬浮窗）
            self._show_word_overlays(word_translations, x, y)

        except Exception as e:
            logger.error(f"处理失败: {e}")
            import traceback
            traceback.print_exc()

    def _show_result(self, original: str, translated: str, image, region_x: int, region_y: int, region_w: int, region_h: int):
        """显示结果窗口"""
        overlay_h = 300
        # 悬浮窗位于截图区域上方，水平居中
        overlay_x = region_x + region_w // 2 - 300
        overlay_y = max(0, region_y - overlay_h - 10)
        window = DesktopOverlay(
            original_text=original,
            translated_text=translated,
            x=overlay_x, y=overlay_y
        )
        window.show(auto_close_delay=config.AUTO_CLOSE_DELAY)

    def _show_word_overlays(self, word_translations, offset_x: int, offset_y: int):
        """为每个单词显示悬浮翻译"""
        import threading

        def show_overlay(word, translated, wx, wy, ww, wh):
            """显示单个单词的悬浮窗"""
            try:
                overlay = WordOverlay(
                    original_word=word,
                    translated_word=translated,
                    x=offset_x + wx,
                    y=offset_y + wy - 40  # 悬浮在单词上方
                )
                overlay.show(auto_close_delay=config.AUTO_CLOSE_DELAY)
            except Exception as e:
                logger.error(f"显示单词悬浮窗失败: {e}")

        # 为每个单词创建悬浮窗（在新线程中执行）
        for word, translated, wx, wy, ww, wh in word_translations:
            t = threading.Thread(target=show_overlay, args=(word, translated, wx, wy, ww, wh), daemon=True)
            t.start()

    def start(self, hotkey: str = None):
        """
        启动监听

        Args:
            hotkey: 快捷键，如 "ctrl+alt+f"
        """
        if hotkey is None:
            hotkey = config.HOTKEY

        try:
            import keyboard
        except ImportError:
            logger.error("keyboard库未安装，请运行: pip install keyboard")
            return

        self.running = True
        logger.info(f"屏幕翻译已启动，快捷键: {hotkey}")
        logger.info("按 Esc 键可退出程序")

        def on_trigger():
            if self.running:
                # 在新线程中执行，避免阻塞快捷键监听
                thread = threading.Thread(target=self.capture_and_translate, daemon=True)
                thread.start()

        def on_exit():
            logger.info("正在退出...")
            self.running = False
            sys.exit(0)

        # 注册快捷键
        keyboard.add_hotkey(hotkey, on_trigger)
        keyboard.add_hotkey('esc', on_exit)

        # 保持主线程运行
        try:
            while self.running:
                time.sleep(0.5)
        except KeyboardInterrupt:
            self.running = False
            logger.info("程序已退出")


def main():
    """主入口"""
    logger.info("=" * 50)
    logger.info("屏幕翻译工具")
    logger.info("=" * 50)

    # 检查依赖
    missing_deps = []

    try:
        import mss
    except ImportError:
        missing_deps.append("mss")

    try:
        import pytesseract
    except ImportError:
        missing_deps.append("pytesseract")

    try:
        import PIL
    except ImportError:
        missing_deps.append("Pillow")

    try:
        import keyboard
    except ImportError:
        missing_deps.append("keyboard")

    try:
        import deep_translator
    except ImportError:
        missing_deps.append("deep-translator")

    if missing_deps:
        logger.error(f"缺少以下依赖: {', '.join(missing_deps)}")
        logger.info("请运行: pip install " + " ".join(missing_deps))
        sys.exit(1)

    # 检查Tesseract
    version = OCREngine.get_tesseract_version()
    if version:
        logger.info(f"Tesseract版本: {version}")
    else:
        logger.warning("未检测到Tesseract，OCR功能可能不可用")
        logger.info("请从 https://github.com/UB-Mannheim/tesseract/releases 下载安装")

    # 显示可用OCR语言
    langs = OCREngine.get_available_languages()
    if langs:
        logger.info(f"可用的OCR语言: {', '.join(langs)}")

    # 启动翻译器
    translator = ScreenTranslator()
    translator.start()


if __name__ == "__main__":
    main()
