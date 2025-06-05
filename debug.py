import sys
import traceback
from tkinter import Tk, Label, messagebox

def show_error_window(error_message):
    root = Tk()
    root.title("错误信息")
    root.geometry("600x400")
    Label(root, text=error_message, justify="left", wraplength=550).pack(padx=20, pady=20)
    root.mainloop()

try:
    print("开始导入模块...")
    import tkinter as tk
    from tkinter import ttk
    print("tkinter 导入成功")
    
    from database import DatabaseManager
    print("DatabaseManager 导入成功")
    
    print("初始化数据库...")
    db = DatabaseManager()
    print("数据库初始化成功")
    
    print("创建主窗口...")
    root = tk.Tk()
    root.title("库存管理系统 - 调试模式")
    root.geometry("300x200")
    
    label = tk.Label(root, text="系统正在运行")
    label.pack(pady=20)
    
    print("窗口创建成功，开始主循环")
    root.mainloop()
    print("程序正常结束")

except Exception as e:
    error_msg = f"错误类型: {type(e).__name__}\n"
    error_msg += f"错误信息: {str(e)}\n\n"
    error_msg += "详细错误追踪:\n"
    error_msg += traceback.format_exc()
    
    print(error_msg)  # 在控制台打印错误
    show_error_window(error_msg)  # 显示错误窗口 