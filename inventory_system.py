import tkinter as tk
from tkinter import ttk, messagebox
from database import DatabaseManager

class InventorySystem:
    def __init__(self, root):
        self.root = root
        self.root.title("库存管理系统")
        self.root.geometry("1200x600")  # 增加窗口宽度
        
        # 初始化数据库
        self.db = DatabaseManager()
        
        # 创建主框架
        self.create_widgets()
        
        # 刷新商品列表
        self.refresh_product_list()
    
    def create_widgets(self):
        # 左侧商品列表
        list_frame = ttk.LabelFrame(self.root, text="商品列表", padding="5")
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建表格
        columns = ("ID", "名称", "数量", "价格", "描述")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # 设置列标题
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
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
        
        ttk.Label(inventory_frame, text="数量:").grid(row=0, column=0, sticky=tk.W)
        self.inventory_quantity_var = tk.StringVar()
        ttk.Entry(inventory_frame, textvariable=self.inventory_quantity_var).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(inventory_frame, text="备注:").grid(row=1, column=0, sticky=tk.W)
        self.remark_var = tk.StringVar()
        ttk.Entry(inventory_frame, textvariable=self.remark_var).grid(row=1, column=1, padx=5, pady=2)
        
        inventory_buttons = ttk.Frame(inventory_frame)
        inventory_buttons.grid(row=2, column=0, columnspan=2, pady=5)
        
        ttk.Button(inventory_buttons, text="入库", command=lambda: self.process_inventory('in')).pack(side=tk.LEFT, padx=5)
        ttk.Button(inventory_buttons, text="出库", command=lambda: self.process_inventory('out')).pack(side=tk.LEFT, padx=5)
        
        # 搜索框
        search_frame = ttk.Frame(operation_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(search_frame, text="搜索", command=self.search_products).pack(side=tk.RIGHT, padx=5)
        
        # 刷新按钮
        ttk.Button(operation_frame, text="刷新列表", command=self.refresh_product_list).pack(fill=tk.X, padx=5, pady=5)
        
        # 绑定表格选择事件
        self.tree.bind('<<TreeviewSelect>>', self.on_select_item)
    
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
            remark = self.remark_var.get()
            
            success, message = self.db.process_inventory(item_id, type, quantity, remark)
            
            if success:
                messagebox.showinfo("成功", message)
                self.clear_inventory_inputs()
                self.refresh_product_list()
            else:
                messagebox.showerror("错误", message)
                
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数量！")
    
    def clear_inventory_inputs(self):
        """清空出入库输入框"""
        self.inventory_quantity_var.set("")
        self.remark_var.set("")
    
    def add_product(self):
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
        keyword = self.search_var.get().strip()
        if keyword:
            products = self.db.search_products(keyword)
        else:
            products = self.db.get_all_products()
        
        self.refresh_product_list(products)
    
    def refresh_product_list(self, products=None):
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 获取并显示商品列表
        if products is None:
            products = self.db.get_all_products()
        
        for product in products:
            self.tree.insert('', tk.END, values=product)
    
    def on_select_item(self, event):
        selected_items = self.tree.selection()
        if selected_items:
            values = self.tree.item(selected_items[0])['values']
            self.name_var.set(values[1])
            self.quantity_var.set(values[2])
            self.price_var.set(values[3])
            self.description_var.set(values[4])
    
    def clear_inputs(self):
        self.name_var.set("")
        self.quantity_var.set("")
        self.price_var.set("")
        self.description_var.set("")
        self.clear_inventory_inputs()

if __name__ == "__main__":
    root = tk.Tk()
    app = InventorySystem(root)
    root.mainloop() 