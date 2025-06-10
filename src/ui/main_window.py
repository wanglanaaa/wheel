"""
主窗口模块
"""
import tkinter as tk
from tkinter import ttk, messagebox
from database.db_manager import DatabaseManager
from ui.inventory_records_window import InventoryRecordsWindow

class InventorySystem:
    """库存管理系统主窗口类"""
    def __init__(self, root):
        self.root = root
        self.root.title("库存管理系统")
        self.root.geometry("1200x600")
        
        # 初始化数据库
        self.db = DatabaseManager()
        
        # 创建主框架
        self.create_widgets()
        
        # 刷新商品列表
        self.refresh_product_list()
    
    def create_widgets(self):
        """创建窗口部件"""
        # 左侧商品列表
        list_frame = ttk.LabelFrame(self.root, text="商品列表", padding="5")
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建表格
        columns = ("ID", "名称", "数量", "价格(均价)", "描述", "更新时间")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # 设置列标题
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # 调整时间列的宽度
        self.tree.column("更新时间", width=150)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 放置表格和滚动条
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 右侧操作区域
        operation_frame = ttk.LabelFrame(self.root, text="操作区", padding="5")
        operation_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)
        
        # 添加商品区域
        add_frame = ttk.LabelFrame(operation_frame, text="添加/修改商品", padding="5")
        add_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 商品信息输入框
        ttk.Label(add_frame, text="商品名称:").grid(row=0, column=0, sticky=tk.W)
        self.name_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.name_var).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(add_frame, text="数量:").grid(row=1, column=0, sticky=tk.W)
        self.quantity_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.quantity_var).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(add_frame, text="价格:").grid(row=2, column=0, sticky=tk.W)
        self.price_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.price_var).grid(row=2, column=1, padx=5, pady=2)
        
        ttk.Label(add_frame, text="描述:").grid(row=3, column=0, sticky=tk.W)
        self.description_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.description_var).grid(row=3, column=1, padx=5, pady=2)
        
        # 按钮区域
        button_frame = ttk.Frame(operation_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="添加商品", command=self.add_product).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="修改商品", command=self.update_product).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="删除商品", command=self.delete_product).pack(fill=tk.X, pady=2)
        
        # 出入库操作区域
        inventory_frame = ttk.LabelFrame(operation_frame, text="出入库操作", padding="5")
        inventory_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 使用Grid布局管理器
        inventory_frame.grid_columnconfigure(1, weight=1)
        inventory_frame.grid_columnconfigure(2, weight=1)
        
        # 数量输入框
        ttk.Label(inventory_frame, text="数量:", width=8).grid(row=0, column=0, sticky=tk.W, padx=(0,5))
        self.inventory_quantity_var = tk.StringVar()
        ttk.Entry(inventory_frame, textvariable=self.inventory_quantity_var).grid(row=0, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=2)
        
        # 价格标签和输入框
        price_frame = ttk.Frame(inventory_frame)
        price_frame.grid(row=1, column=0, columnspan=3, sticky=tk.EW, pady=2)
        price_frame.grid_columnconfigure(1, weight=1)
        
        self.price_label = ttk.Label(price_frame, text="价格:", width=8)
        self.price_label.grid(row=0, column=0, sticky=tk.W)
        
        self.inventory_price_var = tk.StringVar()
        self.price_entry = ttk.Entry(price_frame, textvariable=self.inventory_price_var)
        self.price_entry.grid(row=0, column=1, sticky=tk.EW, padx=5)
        
        # 价格提示标签 - 固定宽度
        self.price_hint = ttk.Label(price_frame, text="", width=20, foreground="gray")
        self.price_hint.grid(row=0, column=2, sticky=tk.W)
        
        # 备注输入框
        ttk.Label(inventory_frame, text="备注:", width=8).grid(row=2, column=0, sticky=tk.W, padx=(0,5))
        self.remark_var = tk.StringVar()
        ttk.Entry(inventory_frame, textvariable=self.remark_var).grid(row=2, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=2)
        
        # 出入库按钮区域
        button_frame = ttk.Frame(inventory_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        # 入库按钮
        self.in_button = ttk.Button(
            button_frame,
            text="入库",
            command=lambda: self.process_inventory('in'),
            width=15
        )
        self.in_button.pack(side=tk.LEFT, padx=5)
        
        # 出库按钮
        self.out_button = ttk.Button(
            button_frame,
            text="出库",
            command=lambda: self.process_inventory('out'),
            width=15
        )
        self.out_button.pack(side=tk.LEFT, padx=5)
        
        # 绑定按钮悬停事件
        self.in_button.bind('<Enter>', lambda e: self.update_price_hint('in'))
        self.out_button.bind('<Enter>', lambda e: self.update_price_hint('out'))
        
        # 绑定价格输入框焦点事件
        self.price_entry.bind('<FocusIn>', self.on_price_focus)
        
        # 搜索框
        search_frame = ttk.Frame(operation_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(search_frame, text="搜索", command=self.search_products).pack(side=tk.RIGHT, padx=5)
        
        # 刷新按钮
        ttk.Button(operation_frame, text="刷新列表", command=self.refresh_product_list).pack(fill=tk.X, padx=5, pady=5)
        
        # 添加统计按钮
        stats_button = ttk.Button(
            operation_frame,
            text="出入库记录统计",
            command=self.show_inventory_records
        )
        stats_button.pack(fill=tk.X, padx=5, pady=5)
        
        # 绑定表格选择事件
        self.tree.bind('<<TreeviewSelect>>', self.on_select_item)
    
    def on_price_focus(self, event):
        """当价格输入框获得焦点时，根据最后悬停的按钮更新提示"""
        if hasattr(self, '_last_hover_type'):
            self.update_price_hint(self._last_hover_type)
    
    def update_price_hint(self, type):
        """更新价格输入提示"""
        self._last_hover_type = type
        if type == 'in':
            self.price_label.configure(text="进价:")
            self.price_hint.configure(text="(选填) 入库成本价")
        else:
            self.price_label.configure(text="售价:")
            self.price_hint.configure(text="(必填) 出库销售价格")
    
    def process_inventory(self, type):
        """处理出入库操作"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择商品！")
            return
        
        try:
            quantity = int(self.inventory_quantity_var.get())
            if quantity <= 0:
                messagebox.showerror("错误", "数量必须大于0！")
                return
            
            item_id = self.tree.item(selected_items[0])['values'][0]
            
            # 获取价格
            price_str = self.inventory_price_var.get().strip()
            
            if type == 'out' and not price_str:
                messagebox.showerror("错误", "出库时必须输入售价！")
                return
            
            try:
                price = float(price_str) if price_str else None
                if price is not None and price < 0:
                    messagebox.showerror("错误", "价格不能为负数！")
                    return
            except ValueError:
                messagebox.showerror("错误", "请输入有效的价格！")
                return
            
            remark = self.remark_var.get()
            
            # 执行数据库操作
            success, message = self.db.process_inventory(item_id, type, quantity, price, remark)
            
            if success:
                messagebox.showinfo("成功", message)
                self.clear_inventory_inputs()
                self.refresh_product_list()
            else:
                messagebox.showerror("错误", message)
        
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数量！")
        except Exception as e:
            messagebox.showerror("错误", f"操作失败: {str(e)}")
    
    def clear_inventory_inputs(self):
        """清空出入库输入框"""
        self.inventory_quantity_var.set("")
        self.inventory_price_var.set("")
        self.remark_var.set("")
        self.price_label.configure(text="价格:")
        self.price_hint.configure(text="")
    
    def add_product(self):
        """添加商品"""
        try:
            name = self.name_var.get().strip()
            quantity = int(self.quantity_var.get())
            price = float(self.price_var.get())
            description = self.description_var.get().strip()
            
            if not name:
                messagebox.showerror("错误", "商品名称不能为空！")
                return
            
            if quantity < 0:
                messagebox.showerror("错误", "数量不能为负数！")
                return
            
            if price < 0:
                messagebox.showerror("错误", "价格不能为负数！")
                return
            
            self.db.add_product(name, quantity, price, description)
            messagebox.showinfo("成功", "商品添加成功！")
            self.clear_inputs()
            self.refresh_product_list()
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数量和价格！")
    
    def update_product(self):
        """更新商品"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择要修改的商品！")
            return
        
        try:
            item_id = self.tree.item(selected_items[0])['values'][0]
            name = self.name_var.get().strip()
            quantity = int(self.quantity_var.get())
            price = float(self.price_var.get())
            description = self.description_var.get().strip()
            
            if not name:
                messagebox.showerror("错误", "商品名称不能为空！")
                return
            
            if quantity < 0:
                messagebox.showerror("错误", "数量不能为负数！")
                return
            
            if price < 0:
                messagebox.showerror("错误", "价格不能为负数！")
                return
            
            self.db.update_product(item_id, name, quantity, price, description)
            messagebox.showinfo("成功", "商品更新成功！")
            self.clear_inputs()
            self.refresh_product_list()
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数量和价格！")
    
    def delete_product(self):
        """删除商品"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择要删除的商品！")
            return
        
        if messagebox.askyesno("确认", "确定要删除选中的商品吗？"):
            item_id = self.tree.item(selected_items[0])['values'][0]
            self.db.delete_product(item_id)
            messagebox.showinfo("成功", "商品删除成功！")
            self.clear_inputs()
            self.refresh_product_list()
    
    def search_products(self):
        """搜索商品"""
        keyword = self.search_var.get().strip()
        products = self.db.search_products(keyword) if keyword else self.db.get_all_products()
        self.refresh_product_list(products)
    
    def refresh_product_list(self, products=None):
        """刷新商品列表"""
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 获取并显示商品列表
        if products is None:
            products = self.db.get_all_products()
        
        for product in products:
            values = (
                product.id,
                product.name,
                product.quantity,
                product.price_display,
                product.description,
                product.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            )
            
            # 如果均价高于当前价格，使用红色显示
            if product.has_high_avg_price:
                self.tree.insert('', tk.END, values=values, tags=('high_avg_price',))
            else:
                self.tree.insert('', tk.END, values=values)
        
        # 设置标签样式
        self.tree.tag_configure('high_avg_price', foreground='red')
    
    def on_select_item(self, event):
        """选择商品时的回调函数"""
        selected_items = self.tree.selection()
        if selected_items:
            values = self.tree.item(selected_items[0])['values']
            self.name_var.set(values[1])
            self.quantity_var.set(values[2])
            self.price_var.set(values[3].split()[0])  # 只取当前价格，不要均价部分
            self.description_var.set(values[4])
    
    def clear_inputs(self):
        """清空输入框"""
        self.name_var.set("")
        self.quantity_var.set("")
        self.price_var.set("")
        self.description_var.set("")
        self.clear_inventory_inputs()
    
    def show_inventory_records(self):
        """显示出入库记录统计窗口"""
        InventoryRecordsWindow(self.root) 