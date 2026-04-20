"""
屏幕截图和区域选择模块
"""

import logging
import os
import tempfile
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

try:
    import mss
    import numpy as np
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False
    logger.warning("mss 未安装")

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.error("PIL 未安装")


class ScreenCapture:
    """屏幕捕获工具"""

    def __init__(self):
        self.sct = mss.mss() if MSS_AVAILABLE else None

    def capture_fullscreen(self) -> Optional[Image.Image]:
        """截取全屏"""
        if not MSS_AVAILABLE:
            logger.error("mss库未安装")
            return None

        try:
            with mss.mss() as sct:
                screenshot = sct.shot()
                img = Image.open(screenshot)
                img.load()  # 确保图片完全加载到内存
                # 清理临时文件
                os.remove(screenshot)
                return img
        except Exception as e:
            logger.error(f"全屏截图失败: {e}")
            return None

    def capture_region(self, region: Tuple[int, int, int, int]) -> Optional[Image.Image]:
        """
        截取指定区域

        Args:
            region: (x, y, width, height)

        Returns:
            区域截图的PIL Image对象
        """
        if not MSS_AVAILABLE:
            logger.error("mss库未安装")
            return None

        x, y, w, h = region
        try:
            with mss.mss() as sct:
                monitor = {"left": x, "top": y, "width": w, "height": h}
                screenshot = sct.grab(monitor)
                img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
                return img
        except Exception as e:
            logger.error(f"区域截图失败: {e}")
            return None

    def get_cursor_position(self) -> Tuple[int, int]:
        """获取当前鼠标位置"""
        try:
            import ctypes
            cursor = ctypes.wintypes.POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(cursor))
            return cursor.x, cursor.y
        except Exception:
            return 0, 0


class RegionSelector:
    """区域选择器 - Tkinter实现"""

    def __init__(self, background_image: Image.Image):
        """
        Args:
            background_image: 背景截图图片
        """
        self.result = None
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.bg_image = background_image
        self.tk_image = None

    def select(self, parent=None) -> Optional[Tuple[int, int, int, int]]:
        """
        让用户选择区域

        Returns:
            (x, y, width, height) 或 None
        """
        try:
            import tkinter as tk
            from tkinter import ttk
        except ImportError:
            logger.error("Tkinter未安装")
            return None

        root = tk.Tk() if parent is None else tk.Toplevel(parent)
        root.attributes('-fullscreen', True)
        root.attributes('-alpha', 0.3)
        root.configure(bg='gray')
        root.cursor("crosshair")

        # 获取屏幕尺寸
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # 创建画布
        canvas = tk.Canvas(root, width=screen_width, height=screen_height,
                          bg='gray', highlightthickness=0)
        canvas.pack(fill='both', expand=True)

        # 将PIL图片转换为Tkinter PhotoImage
        self.tk_image = ImageTk.PhotoImage(self.bg_image)
        canvas.create_image(0, 0, anchor='nw', image=self.tk_image)

        # 半透明遮罩层
        canvas.create_rectangle(0, 0, screen_width, screen_height,
                               fill='gray', stipple='gray50')

        # 说明文字
        canvas.create_text(screen_width // 2, 50,
                          text="拖拽选择区域，按 Enter 确认，Esc 取消",
                          fill='white', font=('微软雅黑', 16))

        def on_mouse_down(event):
            self.start_x = event.x
            self.start_y = event.y
            if self.rect:
                canvas.delete(self.rect)
            self.rect = canvas.create_rectangle(
                self.start_x, self.start_y, self.start_x, self.start_y,
                outline='red', width=2
            )

        def on_mouse_drag(event):
            if self.rect:
                canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

        def on_mouse_up(event):
            pass

        def on_enter(event):
            if self.start_x is not None:
                x1 = min(self.start_x, event.x)
                y1 = min(self.start_y, event.y)
                x2 = max(self.start_x, event.x)
                y2 = max(self.start_y, event.y)
                self.result = (x1, y1, x2 - x1, y2 - y1)
                root.quit()
                root.destroy()

        def on_escape(event):
            self.result = None
            root.quit()
            root.destroy()

        def on_fullscreen(event):
            # Enter键直接全屏
            self.result = (0, 0, screen_width, screen_height)
            root.quit()
            root.destroy()

        canvas.bind('<ButtonPress-1>', on_mouse_down)
        canvas.bind('<B1-Motion>', on_mouse_drag)
        canvas.bind('<ButtonRelease-1>', on_mouse_up)
        canvas.bind('<Return>', on_enter)
        canvas.bind('<Escape>', on_escape)
        canvas.bind('<KP_Enter>', on_enter)

        root.bind('<Return>', on_fullscreen)

        root.focus_force()
        root.mainloop()

        return self.result


def capture_and_select() -> Optional[Tuple[Image.Image, Tuple[int, int, int, int]]]:
    """
    截图并让用户选择区域

    Returns:
        (截图Image对象, 区域(x,y,w,h)) 或 None
    """
    capture = ScreenCapture()
    full_img = capture.capture_fullscreen()
    if full_img is None:
        return None

    selector = RegionSelector(full_img)
    region = selector.select()

    if region is None:
        return None

    return full_img, region


def save_temp_image(img: Image.Image, suffix: str = ".png") -> str:
    """保存图片到临时文件"""
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    img.save(path)
    return path
