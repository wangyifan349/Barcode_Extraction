import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageGrab
import datetime

class ScreenshotTool:
    def __init__(self, root):
        self.root = root
        self.root.title("截屏工具")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        # 创建样式
        style = ttk.Style()
        style.configure("TButton", padding=10, font=('Arial', 12))

        # 创建按钮
        self.screenshot_button = ttk.Button(root, text="选择区域截屏", command=self.select_area)
        self.screenshot_button.pack(pady=50)

        # 状态栏
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor='w')
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_var.set("准备截屏...")

    def select_area(self):
        self.status_var.set("请拖动选择截屏区域...")
        self.root.withdraw()  # 隐藏主窗口
        self.root.after(100, self.start_selection)

    def start_selection(self):
        # 创建一个全屏透明窗口用于选择区域
        self.selection_window = tk.Toplevel(self.root)
        self.selection_window.attributes("-fullscreen", True)
        self.selection_window.attributes("-alpha", 0.3)  # 透明度
        self.selection_window.bind("<ButtonPress-1>", self.on_button_press)
        self.selection_window.bind("<B1-Motion>", self.on_mouse_drag)
        self.selection_window.bind("<ButtonRelease-1>", self.on_button_release)
        self.selection_window.bind("<Escape>", self.cancel_selection)

        self.start_x = None
        self.start_y = None
        self.rect = None

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.selection_window.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red', width=2)

    def on_mouse_drag(self, event):
        if self.rect:
            self.selection_window.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_button_release(self, event):
        self.selection_window.withdraw()  # 隐藏选择窗口
        x1, y1, x2, y2 = self.start_x, self.start_y, event.x, event.y
        self.take_screenshot(x1, y1, x2, y2)

    def cancel_selection(self, event):
        self.selection_window.destroy()
        self.root.deiconify()  # 显示主窗口
        self.status_var.set("截屏已取消")

    def take_screenshot(self, x1, y1, x2, y2):
        # 截取指定区域
        screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        now = datetime.datetime.now()
        filename = f"screenshot_{now.strftime('%Y%m%d_%H%M%S')}.png"
        screenshot.save(filename)
        self.status_var.set(f"截图已保存为 {filename}")
        self.root.deiconify()  # 显示主窗口
        self.selection_window.destroy()  # 关闭选择窗口

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenshotTool(root)
    root.mainloop()
