"""
出入库记录窗口
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import pandas as pd
from ..database.db_manager import DatabaseManager

class InventoryRecordsWindow:
    """出入库记录窗口类"""
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("出入库记录统计")
        self.window.geometry("1000x600")
        
        # 创建主框架
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 添加导出按钮
        ttk.Button(
            button_frame,
            text="导出入库明细",
            command=lambda: self.export_records('in')
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="导出出库明细",
            command=lambda: self.export_records('out')
        ).pack(side=tk.LEFT, padx=5)
        
        # 创建表格框架
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建表格
        columns = ("时间", "商品名称", "类型", "数量", "单价", "成本价", "总价", "毛利", "备注")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        # 设置列标题和宽度
        self.tree.heading("时间", text="时间")
        self.tree.heading("商品名称", text="商品名称")
        self.tree.heading("类型", text="类型")
        self.tree.heading("数量", text="数量")
        self.tree.heading("单价", text="单价")
        self.tree.heading("成本价", text="成本价")
        self.tree.heading("总价", text="总价")
        self.tree.heading("毛利", text="毛利")
        self.tree.heading("备注", text="备注")
        
        self.tree.column("时间", width=150)
        self.tree.column("商品名称", width=150)
        self.tree.column("类型", width=60)
        self.tree.column("数量", width=60)
        self.tree.column("单价", width=100)
        self.tree.column("成本价", width=100)
        self.tree.column("总价", width=100)
        self.tree.column("毛利", width=100)
        self.tree.column("备注", width=140)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 放置表格和滚动条
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 加载数据
        self.load_records()
    
    def export_records(self, record_type: str):
        """导出记录到Excel"""
        try:
            # 获取数据
            db = DatabaseManager()
            records = db.get_inventory_records()
            
            # 筛选指定类型的记录并转换为字典列表
            filtered_records = [
                record.to_dict() for record in records
                if record.type == ('in' if record_type == 'in' else 'out')
            ]
            
            if not filtered_records:
                type_text = "入库" if record_type == "in" else "出库"
                messagebox.showwarning("警告", f"没有{type_text}记录可供导出！")
                return
            
            # 创建DataFrame
            df = pd.DataFrame(filtered_records)
            
            # 获取保存路径
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            type_text = "入库" if record_type == "in" else "出库"
            default_filename = f"{type_text}记录_{current_time}.xlsx"
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel 文件", "*.xlsx")],
                initialfile=default_filename
            )
            
            if file_path:
                # 导出到Excel
                df.to_excel(file_path, index=False, engine='openpyxl')
                messagebox.showinfo("成功", f"{type_text}记录已导出到：\n{file_path}")
        
        except Exception as e:
            messagebox.showerror("错误", f"导出失败：{str(e)}")
    
    def load_records(self):
        """加载记录到表格"""
        # 获取数据库实例
        db = DatabaseManager()
        records = db.get_inventory_records()
        
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 填充数据
        total_profit = 0  # 总毛利
        for record in records:
            # 计算总毛利
            if record.type == 'out' and record.profit is not None:
                total_profit += record.profit
            
            # 格式化价格显示
            unit_price = f"¥{record.price:.2f}" if record.price is not None else "-"
            cost_price = f"¥{record.cost_price:.2f}" if record.cost_price is not None else "-"
            total_price = f"¥{record.total_price:.2f}" if record.total_price != 0 else "-"
            profit = f"¥{record.profit:.2f}" if record.profit is not None else "-"
            
            values = (
                record.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                record.product_name,
                record.type_text,
                record.quantity,
                unit_price,
                cost_price,
                total_price,
                profit,
                record.remark or "-"
            )
            
            # 使用不同的颜色标识出入库记录
            tag = "in_record" if record.type == "in" else "out_record"
            self.tree.insert("", 0, values=values, tags=(tag,))
        
        # 设置标签样式
        self.tree.tag_configure("in_record", foreground="green")
        self.tree.tag_configure("out_record", foreground="red")
        
        # 添加总计行
        self.tree.insert("", tk.END, values=(
            "总计", "", "", "", "", "", "", f"¥{total_profit:.2f}", ""
        ), tags=('total',))
        self.tree.tag_configure('total', background='#f0f0f0', foreground='blue') 