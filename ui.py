"""
结果展示窗口 - Tkinter实现
"""

import logging
import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional
import pyperclip

logger = logging.getLogger(__name__)


class DesktopOverlay:
    """桌面悬浮翻译层 - 透明、无边框、置顶"""

    def __init__(self, original_text: str, translated_text: str, x: int = 100, y: int = 100):
        self.original_text = original_text
        self.translated_text = translated_text
        self.x = x
        self.y = y
        self.root = None
        self.drag_data = {"x": 0, "y": 0}

    def show(self, auto_close_delay: int = 0):
        """显示悬浮层"""
        try:
            self._create_window()
            if auto_close_delay > 0:
                self.root.after(auto_close_delay * 1000, self.close)
            self.root.mainloop()
        except Exception as e:
            logger.error(f"显示悬浮层失败: {e}")

    def _create_window(self):
        """创建悬浮窗"""
        self.root = tk.Tk()
        self.root.overrideredirect(True)  # 无边框
        self.root.attributes('-topmost', True)  # 置顶
        self.root.attributes('-alpha', 0.9)  # 透明度
        self.root.configure(bg='white')

        # 半透明背景
        self.root.attributes('-transparentcolor', 'white')

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # 窗口尺寸
        text_width = min(600, screen_width - self.x - 50)
        window_height = 300

        self.root.geometry(f"{text_width}x{window_height}+{self.x}+{self.y}")

        # 可拖动
        def on_drag_start(event):
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

        def on_drag_motion(event):
            delta_x = event.x - self.drag_data["x"]
            delta_y = event.y - self.drag_data["y"]
            new_x = self.root.winfo_x() + delta_x
            new_y = self.root.winfo_y() + delta_y
            self.root.geometry(f"+{new_x}+{new_y}")

        # 顶部拖动栏
        drag_bar = tk.Frame(self.root, bg='#3498db', height=25)
        drag_bar.pack(fill='x')
        drag_bar.bind('<Button-1>', on_drag_start)
        drag_bar.bind('<B1-Motion>', on_drag_motion)

        # 拖动提示
        tk.Label(drag_bar, text="翻译结果  -  拖动移动  -  Esc关闭",
                bg='#3498db', fg='white', font=('微软雅黑', 9)).pack(side='left', padx=5)

        # 关闭按钮
        tk.Label(drag_bar, text='×', bg='#3498db', fg='white',
                font=('Arial', 14, 'bold'), cursor='hand2').pack(side='right', padx=5)
        drag_bar.bind('<Button-1>', lambda e: self.close())

        # 内容区
        content = tk.Frame(self.root, bg='white')
        content.pack(fill='both', expand=True, padx=5, pady=5)

        # 原文
        tk.Label(content, text="原文:", bg='white', fg='#555',
                font=('微软雅黑', 9, 'bold'), anchor='w').pack(fill='x')
        original_label = tk.Label(content, text=self.original_text[:200],
                bg='#f8f8f8', fg='#333', font=('微软雅黑', 10),
                anchor='nw', justify='left', wraplength=text_width - 20)
        original_label.pack(fill='x', pady=(0, 5))

        # 译文
        tk.Label(content, text="译文:", bg='white', fg='#2980b9',
                font=('微软雅黑', 9, 'bold'), anchor='w').pack(fill='x')
        translated_label = tk.Label(content, text=self.translated_text[:200],
                bg='#e8f4fd', fg='#1a5276', font=('微软雅黑', 12),
                anchor='nw', justify='left', wraplength=text_width - 20)
        translated_label.pack(fill='both', expand=True, pady=(0, 5))

        # 底部按钮
        btn_frame = tk.Frame(content, bg='white')
        btn_frame.pack(fill='x')

        def copy_translated():
            pyperclip.copy(self.translated_text)
            logger.info("已复制到剪贴板")

        tk.Button(btn_frame, text="复制译文", command=copy_translated,
                bg='#3498db', fg='white', relief='flat',
                font=('微软雅黑', 9), cursor='hand2').pack(side='left')

        tk.Button(btn_frame, text="关闭", command=self.close,
                bg='#e74c3c', fg='white', relief='flat',
                font=('微软雅黑', 9), cursor='hand2').pack(side='right')

        # Esc关闭
        self.root.bind('<Escape>', lambda e: self.close())
        self.root.focus_force()

    def close(self):
        """关闭悬浮窗"""
        if self.root:
            self.root.destroy()
            self.root = None


class WordOverlay:
    """单词悬浮翻译层 - 显示单个单词的翻译"""

    def __init__(self, original_word: str, translated_word: str, x: int, y: int):
        self.original_word = original_word
        self.translated_word = translated_word
        self.x = x
        self.y = y
        self.root = None

    def show(self, auto_close_delay: int = 0):
        """显示悬浮层"""
        try:
            self._create_window()
            if auto_close_delay > 0:
                self.root.after(auto_close_delay * 1000, self.close)
            self.root.mainloop()
        except Exception as e:
            logger.error(f"显示单词悬浮层失败: {e}")

    def _create_window(self):
        """创建悬浮窗"""
        self.root = tk.Tk()
        self.root.overrideredirect(True)  # 无边框
        self.root.attributes('-topmost', True)  # 置顶
        self.root.attributes('-alpha', 0.85)

        # 根据文字长度调整窗口大小
        text = self.translated_word
        char_width = 14
        window_width = max(len(text) * char_width + 10, 40)
        window_height = 28

        # 确保不超出屏幕
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        if self.x + window_width > screen_width:
            self.x = screen_width - window_width - 10
        if self.y < 0:
            self.y = 0

        self.root.geometry(f"{window_width}x{window_height}+{self.x}+{self.y}")

        # 背景框架
        frame = tk.Frame(self.root, bg='#2c3e50', padx=3, pady=1)
        frame.pack(fill='both', expand=True)

        # 翻译文字
        label = tk.Label(frame, text=text, bg='#2c3e50', fg='white',
                        font=('微软雅黑', 11), anchor='center')
        label.pack(fill='both', expand=True)

        # 点击关闭
        frame.bind('<Button-1>', lambda e: self.close())
        label.bind('<Button-1>', lambda e: self.close())
        self.root.bind('<Escape>', lambda e: self.close())
        self.root.bind('<Button-1>', lambda e: self.close())
        self.root.focus_force()

    def close(self):
        """关闭悬浮窗"""
        if self.root:
            self.root.destroy()
            self.root = None

try:
    from PIL import Image, ImageTk, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class ResultWindow:
    """结果显示窗口"""

    def __init__(self, original_text: str, translated_text: str,
                 source_image: Optional[Image.Image] = None,
                 opacity: float = 0.95):
        """
        Args:
            original_text: 原文
            translated_text: 译文
            source_image: 截图（可选，用于显示缩略图）
            opacity: 窗口透明度
        """
        self.original_text = original_text
        self.translated_text = translated_text
        self.source_image = source_image
        self.opacity = opacity
        self.root = None

    def show(self, auto_close_delay: int = 0):
        """
        显示结果窗口

        Args:
            auto_close_delay: 自动关闭延迟（秒），0表示不自动关闭
        """
        try:
            self._create_window()

            if auto_close_delay > 0:
                self.root.after(auto_close_delay * 1000, self.close)

            self.root.mainloop()
        except Exception as e:
            logger.error(f"显示结果窗口失败: {e}")

    def _create_window(self):
        """创建窗口"""
        self.root = tk.Tk()
        self.root.title("翻译结果")

        # 设置窗口大小和位置
        window_width = 500
        window_height = 450
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # 设置透明度
        try:
            self.root.attributes('-alpha', self.opacity)
        except Exception:
            pass

        # 设置样式
        style = ttk.Style()
        style.configure('Title.TLabel', font=('微软雅黑', 12, 'bold'))
        style.configure('Normal.TLabel', font=('微软雅黑', 10))
        style.configure('Copy.TButton', font=('微软雅黑', 9))

        # 主容器
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill='both', expand=True)

        # 标题
        title_label = ttk.Label(main_frame, text="翻译结果", style='Title.TLabel')
        title_label.pack(pady=(0, 10))

        # 如果有截图，显示缩略图
        if self.source_image and PIL_AVAILABLE:
            self._add_image_preview(main_frame)

        # 原文区域
        original_frame = ttk.LabelFrame(main_frame, text="原文", padding=5)
        original_frame.pack(fill='x', pady=(5, 5))

        original_text = scrolledtext.ScrolledText(
            original_frame, height=5, wrap='word',
            font=('微软雅黑', 10), relief='flat'
        )
        original_text.insert('1.0', self.original_text)
        original_text.configure(state='disabled')
        original_text.pack(fill='x')

        # 复制原文按钮
        ttk.Button(original_frame, text="复制原文",
                  command=lambda: self._copy_text(self.original_text),
                  style='Copy.TButton').pack(anchor='e', pady=(5, 0))

        # 译文区域
        translated_frame = ttk.LabelFrame(main_frame, text="译文", padding=5)
        translated_frame.pack(fill='both', expand=True, pady=(5, 5))

        translated_text = scrolledtext.ScrolledText(
            translated_frame, height=6, wrap='word',
            font=('微软雅黑', 10), relief='flat'
        )
        translated_text.insert('1.0', self.translated_text)
        translated_text.configure(state='disabled')
        translated_text.pack(fill='both', expand=True)

        # 复制译文按钮
        ttk.Button(translated_frame, text="复制译文",
                  command=lambda: self._copy_text(self.translated_text),
                  style='Copy.TButton').pack(anchor='e', pady=(5, 0))

        # 底部按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))

        ttk.Button(button_frame, text="关闭 (Esc)",
                  command=self.close).pack(side='right')

        # 绑定Esc键
        self.root.bind('<Escape>', lambda e: self.close())

        # 窗口关闭时清理
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def _add_image_preview(self, parent):
        """添加截图预览"""
        try:
            # 缩放图片以适应窗口
            max_width = 460
            max_height = 150
            img = self.source_image.copy()

            # 计算缩放比例
            ratio = min(max_width / img.width, max_height / img.height)
            if ratio < 1:
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            # 添加红色边框标注区域（如果有的话）
            # 这里简化处理

            self.tk_thumbnail = ImageTk.PhotoImage(img)

            img_label = ttk.Label(parent, image=self.tk_thumbnail)
            img_label.pack(pady=(0, 10))
        except Exception as e:
            logger.warning(f"添加图片预览失败: {e}")

    def _copy_text(self, text: str):
        """复制文本到剪贴板"""
        try:
            pyperclip.copy(text)
            # 显示提示（临时改变按钮文字）
            logger.info("已复制到剪贴板")
        except Exception as e:
            logger.error(f"复制失败: {e}")

    def close(self):
        """关闭窗口"""
        if self.root:
            self.root.destroy()
            self.root = None


class SelectionOverlay:
    """全屏选择覆盖层"""

    def __init__(self):
        self.result = None
        self.root = None

    def wait_for_selection(self) -> Optional[tuple]:
        """等待用户选择区域，返回 (x, y, w, h) 或 None"""
        try:
            import tkinter as tk
        except ImportError:
            return None

        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)
        self.root.configure(bg='gray')
        self.root.cursor("crosshair")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        canvas = tk.Canvas(self.root, width=screen_width, height=screen_height,
                          bg='gray', highlightthickness=0)
        canvas.pack(fill='both', expand=True)

        # 遮罩
        canvas.create_rectangle(0, 0, screen_width, screen_height,
                               fill='gray', stipple='gray50')

        # 提示
        canvas.create_text(screen_width // 2, 50,
                          text="拖拽选择区域，按 Enter 确认全屏，Esc 取消",
                          fill='white', font=('Arial', 16))

        rect = [None]

        def on_press(event):
            rect[0] = canvas.create_rectangle(event.x, event.y, event.x, event.y,
                                              outline='red', width=2)

        def on_drag(event):
            if rect[0]:
                canvas.coords(rect[0], rect[0], event.x, event.y, canvas.coords(rect[0])[0], canvas.coords(rect[0])[1])
                # 简单处理：直接重绘
                canvas.delete(rect[0])
                rect[0] = canvas.create_rectangle(
                    canvas.coords(rect[0])[0], canvas.coords(rect[0])[1],
                    event.x, event.y, outline='red', width=2
                ) if False else None

        def on_release(event):
            if rect[0]:
                coords = canvas.coords(rect[0])
                x1, y1 = coords[0], coords[1]
                x2, y2 = coords[2], coords[3]
                self.result = (int(min(x1, x2)), int(min(y1, y2)),
                              int(abs(x2 - x1)), int(abs(y2 - y1)))
                self.root.quit()

        def on_enter(event):
            self.result = (0, 0, screen_width, screen_height)
            self.root.quit()

        def on_escape(event):
            self.result = None
            self.root.quit()

        canvas.bind('<ButtonPress-1>', on_press)
        canvas.bind('<B1-Motion>', on_drag)
        canvas.bind('<ButtonRelease-1>', on_release)
        canvas.bind('<Return>', on_enter)
        canvas.bind('<Escape>', on_escape)
        canvas.bind('<KP_Enter>', on_enter)

        self.root.focus_force()
        self.root.mainloop()
        self.root.destroy()
        return self.result
