"""
主程序入口
"""
import tkinter as tk
from ui.main_window import InventorySystem

def main():
    """程序入口函数"""
    root = tk.Tk()
    app = InventorySystem(root)
    root.mainloop()

if __name__ == "__main__":
    main() 