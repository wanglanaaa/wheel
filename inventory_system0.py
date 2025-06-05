import tkinter as tk
from tkinter import messagebox

class InventorySystem:
    def __init__(self, root):
        self.root = root
        self.root.title("库存管理系统")
        self.root.geometry("800x600")
        
        # 创建主框架
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # 创建标题标签
        self.title_label = tk.Label(
            self.main_frame,
            text="欢迎使用库存管理系统",
            font=("Arial", 24, "bold")
        )
        self.title_label.pack(pady=20)
        
        # 创建按钮框架
        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.pack(pady=30)
        
        # 创建库存管理按钮
        self.inventory_button = tk.Button(
            self.button_frame,
            text="库存管理",
            font=("Arial", 14),
            width=20,
            height=2,
            command=self.open_inventory
        )
        self.inventory_button.pack(pady=10)
        
        # 创建退出按钮
        self.exit_button = tk.Button(
            self.button_frame,
            text="退出系统",
            font=("Arial", 14),
            width=20,
            height=2,
            command=self.root.quit
        )
        self.exit_button.pack(pady=10)
    
    def open_inventory(self):
        messagebox.showinfo("提示", "库存管理功能即将开放！")

if __name__ == "__main__":
    root = tk.Tk()
    app = InventorySystem(root)
    root.mainloop() 