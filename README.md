# 屏幕翻译工具

快捷键触发截图 → OCR识别 → 在线翻译 → 结果展示

## 功能特性

- 快捷键触发（可自定义）
- 全屏截图 + 区域选择
- 离线OCR识别（Tesseract）
- 多翻译源支持（Google/DeepL/Microsoft）
- 译文一键复制

---

## 环境准备

### 1. 创建Anaconda环境

```bash
conda create -n screen_translate python=3.10
conda activate screen_translate
```

### 2. 安装Tesseract OCR

**Windows:**
1. 下载: https://github.com/UB-Mannheim/tesseract/releases
2. 安装时选择 **中文简体** 语言包
3. 默认安装路径: `C:\Program Files\Tesseract-OCR`

### 3. 安装Python依赖

```bash
cd screen_translate
pip install -r requirements.txt
```

---

## 使用方法

### 基本使用

```bash
python main.py
```

- 按 `Ctrl+Alt+F` 触发截图
- 拖拽选择翻译区域，按 `Enter` 全屏翻译，`Esc` 取消
- 窗口显示原文和译文

### 修改快捷键

编辑 `config.py`:

```python
HOTKEY = "ctrl+shift+t"  # 改为你想要的快捷键
```

快捷键格式参考: https://github.com/moses-palmer/pyscreeze

### 修改目标语言

编辑 `config.py`:

```python
TARGET_LANGUAGE = "zh"    # 中文
TARGET_LANGUAGE = "ja"    # 日语
TARGET_LANGUAGE = "ko"    # 韩语
```

### 使用DeepL翻译

1. 获取API Key: https://www.deepl.com/pro-api
2. 编辑 `config.py`:

```python
TRANSLATOR_PROVIDER = "deepl"
DEEPL_API_KEY = "你的API密钥"
```

---

## 打包为EXE

### 使用 auto-py-to-exe

```bash
pip install auto-py-to-exe
auto-py-to-exe
```

打包配置:
- **Onefile**: One Directory（方便包含Tesseract）
- **Additional Files**: 添加Tesseract-OCR文件夹
- **Advanced → --onefile**: 视情况选择

### 打包后运行

如果Tesseract不在默认路径，编辑 `config.py`:

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\path\to\tesseract.exe"
```

---

## 目录结构

```
screen_translate/
├── main.py          # 主入口
├── config.py        # 配置文件
├── capture.py       # 截图和区域选择
├── ocr_engine.py    # OCR识别
├── translator.py    # 翻译引擎
├── ui.py            # 结果窗口
├── requirements.txt # 依赖列表
└── README.md        # 说明文档
```

---

## 常见问题

### Tesseract未找到

确保已安装Tesseract并在 `config.py` 中配置路径:

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

### OCR识别率低

1. 确保选择区域文字清晰
2. 检查 `config.py` 中 `OCR_LANGUAGES` 是否包含目标语言
3. 截图时避免过多背景干扰

### 翻译失败

- 检查网络连接
- Google翻译不稳定时可换用DeepL
- 确认API Key正确（如果使用DeepL）

---

## 技术栈

| 模块 | 技术 |
|------|------|
| 截图 | mss |
| OCR | Tesseract + pytesseract |
| 翻译 | deep-translator |
| 界面 | Tkinter |
| 快捷键 | keyboard |
