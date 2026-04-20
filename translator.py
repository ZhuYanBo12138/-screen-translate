"""
翻译引擎 - 支持多个翻译源
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from deep_translator import GoogleTranslator, DeeplTranslator, MicrosoftTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
    logger.warning("deep-translator 未安装，翻译功能不可用")


class Translator:
    """翻译器封装"""

    def __init__(self, provider: str = "google", target_lang: str = "en", api_key: str = ""):
        """
        Args:
            provider: 翻译源 ("google", "deepL", "microsoft")
            target_lang: 目标语言代码
            api_key: API密钥（DeepL和ChatGPT需要）
        """
        self.provider = provider.lower()
        self.target_lang = target_lang
        self.api_key = api_key

    def translate(self, text: str, source_lang: str = "auto") -> Optional[str]:
        """
        翻译文本

        Args:
            text: 待翻译文本
            source_lang: 源语言代码，默认自动检测

        Returns:
            翻译后的文本，失败返回None
        """
        if not text or not text.strip():
            return None

        if not TRANSLATOR_AVAILABLE:
            logger.error("deep-translator 库未安装")
            return None

        try:
            if self.provider == "google":
                return self._translate_google(text, source_lang)
            elif self.provider == "deepl":
                return self._translate_deepl(text, source_lang)
            elif self.provider == "microsoft":
                return self._translate_microsoft(text, source_lang)
            else:
                logger.error(f"不支持的翻译源: {self.provider}")
                return None
        except Exception as e:
            logger.error(f"翻译失败: {e}")
            return None

    def _translate_google(self, text: str, source_lang: str) -> Optional[str]:
        """Google翻译"""
        try:
            translator = GoogleTranslator(source=source_lang, target=self.target_lang)
            return translator.translate(text)
        except Exception as e:
            logger.error(f"Google翻译出错: {e}")
            return None

    def _translate_deepl(self, text: str, source_lang: str) -> Optional[str]:
        """DeepL翻译"""
        if not self.api_key:
            logger.error("DeepL需要API密钥，请在config.py中设置DEEPL_API_KEY")
            return None
        try:
            translator = DeeplTranslator(api_key=self.api_key, source=source_lang if source_lang != "auto" else None, target=self.target_lang)
            return translator.translate(text)
        except Exception as e:
            logger.error(f"DeepL翻译出错: {e}")
            return None

    def _translate_microsoft(self, text: str, source_lang: str) -> Optional[str]:
        """Microsoft翻译"""
        try:
            translator = MicrosoftTranslator(source=source_lang, target=self.target_lang)
            return translator.translate(text)
        except Exception as e:
            logger.error(f"Microsoft翻译出错: {e}")
            return None


def translate_text(text: str, target_lang: str = "en", provider: str = "google",
                   source_lang: str = "auto", api_key: str = "") -> Optional[str]:
    """
    便捷翻译函数

    Args:
        text: 待翻译文本
        target_lang: 目标语言
        provider: 翻译源
        source_lang: 源语言
        api_key: API密钥

    Returns:
        翻译后的文本
    """
    translator = Translator(provider=provider, target_lang=target_lang, api_key=api_key)
    return translator.translate(text, source_lang)
