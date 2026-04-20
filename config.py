"""
配置文件 - 用户可自定义快捷键和语言设置
"""

# 默认快捷键
HOTKEY = "ctrl+alt+f"

# 截图后是否自动全屏（True=直接识别全屏，False=让用户框选区域）
FULLSCREEN_CAPTURE = True

# OCR语言（chi_sim=简体中文，eng=英文，jpn=日语等，多语言用+连接）
OCR_LANGUAGES = "chi_sim+eng"

# 翻译源
# 可选: "google", "deepL", "chatgpt", "microsoft"
TRANSLATOR_PROVIDER = "google"

# DeepL API密钥（如果使用DeepL翻译）
DEEPL_API_KEY = ""

# 翻译目标语言
TARGET_LANGUAGE = "zh-CN"

# 结果窗口在屏幕上停留时间（秒），0=不自动关闭
AUTO_CLOSE_DELAY = 0

# 窗口透明度 (0.0-1.0)
WINDOW_OPACITY = 0.95

# 日志级别: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL = "INFO"
