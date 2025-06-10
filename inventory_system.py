import tkinter as tk
from tkinter import ttk, messagebox
from database import DatabaseManager

class InventoryRecordsWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("出入库记录统计")
        self.window.geometry("1000x600")  # 加宽窗口以适应新增列
        
        # 创建表格
        columns = ("时间", "商品名称", "类型", "数量", "单价", "成本价", "总价", "毛利", "备注")
        self.tree = ttk.Treeview(self.window, columns=columns, show="headings")
        
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
        scrollbar = ttk.Scrollbar(self.window, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 放置表格和滚动条
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 加载数据
        self.load_records()
    
    def load_records(self):
        # 获取数据库实例
        db = DatabaseManager()
        records = db.get_inventory_records()
        
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 填充数据
        total_profit = 0  # 总毛利
        for record in records:
            # record: id, product_id, type, quantity, price, cost_price, remark, created_at, name, local_time
            type_text = "入库" if record[2] == "in" else "出库"
            price = record[4]  # 入库价/售价
            cost_price = record[5]  # 成本价
            quantity = record[3]
            
            # 格式化价格显示
            if record[2] == 'in':
                # 入库记录
                unit_price = f"¥{price:.2f}" if price is not None else "-"
                cost_price_text = "-"
                total_price = f"¥{price * quantity:.2f}" if price is not None else "-"
                profit = "-"
            else:
                # 出库记录
                unit_price = f"¥{price:.2f}" if price is not None else "-"
                cost_price_text = f"¥{cost_price:.2f}" if cost_price is not None else "-"
                total_price = f"¥{price * quantity:.2f}" if price is not None else "-"
                if price is not None and cost_price is not None:
                    profit_value = (price - cost_price) * quantity
                    total_profit += profit_value
                    profit = f"¥{profit_value:.2f}"
                else:
                    profit = "-"
            
            values = (
                record[9].split('.')[0],  # local_time（去除毫秒）
                record[8],  # name
                type_text,
                quantity,
                unit_price,
                cost_price_text,
                total_price,
                profit,
                record[6] or "-"  # remark
            )
            
            # 使用不同的颜色标识出入库记录
            tag = "in_record" if record[2] == "in" else "out_record"
            self.tree.insert("", 0, values=values, tags=(tag,))
        
        # 设置标签样式
        self.tree.tag_configure("in_record", foreground="green")
        self.tree.tag_configure("out_record", foreground="red")
        
        # 添加总计行
        self.tree.insert("", tk.END, values=(
            "总计", "", "", "", "", "", "", f"¥{total_profit:.2f}", ""
        ), tags=('total',))
        self.tree.tag_configure('total', background='#f0f0f0', foreground='blue')

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
        
        # 数量输入框
        ttk.Label(inventory_frame, text="数量:").grid(row=0, column=0, sticky=tk.W)
        self.inventory_quantity_var = tk.StringVar()
        ttk.Entry(inventory_frame, textvariable=self.inventory_quantity_var).grid(row=0, column=1, padx=5, pady=2)
        
        # 价格标签和输入框
        self.price_label = ttk.Label(inventory_frame, text="价格:")
        self.price_label.grid(row=1, column=0, sticky=tk.W)
        self.inventory_price_var = tk.StringVar()
        self.price_entry = ttk.Entry(inventory_frame, textvariable=self.inventory_price_var)
        self.price_entry.grid(row=1, column=1, padx=5, pady=2)
        
        # 价格说明标签
        self.price_hint = ttk.Label(inventory_frame, text="", foreground="gray")
        self.price_hint.grid(row=1, column=2, sticky=tk.W, padx=5)
        
        # 备注输入框
        ttk.Label(inventory_frame, text="备注:").grid(row=2, column=0, sticky=tk.W)
        self.remark_var = tk.StringVar()
        ttk.Entry(inventory_frame, textvariable=self.remark_var).grid(row=2, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=2)
        
        # 出入库按钮区域
        inventory_buttons = ttk.Frame(inventory_frame)
        inventory_buttons.grid(row=3, column=0, columnspan=3, pady=5)
        
        # 入库按钮
        self.in_button = ttk.Button(
            inventory_buttons,
            text="入库",
            command=lambda: self.process_inventory('in')
        )
        self.in_button.pack(side=tk.LEFT, padx=5)
        
        # 出库按钮
        self.out_button = ttk.Button(
            inventory_buttons,
            text="出库",
            command=lambda: self.process_inventory('out')
        )
        self.out_button.pack(side=tk.LEFT, padx=5)
        
        # 绑定按钮悬停事件
        self.in_button.bind('<Enter>', lambda e: self.update_price_hint('in'))
        self.in_button.bind('<Leave>', lambda e: self.clear_price_hint())
        self.out_button.bind('<Enter>', lambda e: self.update_price_hint('out'))
        self.out_button.bind('<Leave>', lambda e: self.clear_price_hint())
        
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
    
    def update_price_hint(self, type):
        """更新价格输入提示"""
        if type == 'in':
            self.price_label.configure(text="进价:")
            self.price_hint.configure(text="(选填) 入库成本价")
        else:
            self.price_label.configure(text="售价:")
            self.price_hint.configure(text="(必填) 出库销售价格")
    
    def clear_price_hint(self):
        """清除价格输入提示"""
        self.price_label.configure(text="价格:")
        self.price_hint.configure(text="")
    
    def process_inventory(self, type):
        """处理出入库操作"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择商品！")
            return
        
        try:
            print(f"开始处理{'入库' if type == 'in' else '出库'}操作...")
            print(f"输入数据: 数量={self.inventory_quantity_var.get()}, 价格={self.inventory_price_var.get()}, 备注={self.remark_var.get()}")
            
            quantity = int(self.inventory_quantity_var.get())
            if quantity <= 0:
                messagebox.showerror("错误", "数量必须大于0！")
                return
            
            item_id = self.tree.item(selected_items[0])['values'][0]
            print(f"选中商品ID: {item_id}")
            
            # 获取价格
            try:
                price_str = self.inventory_price_var.get().strip()
                print(f"价格输入值: {price_str}")
                
                if type == 'in':
                    # 入库时，如果没有输入价格，使用当前商品价格
                    if not price_str:
                        current_item = self.db.get_product(item_id)
                        price = current_item[3] if current_item else None
                        print(f"使用当前商品价格: {price}")
                    else:
                        price = float(price_str)
                else:
                    # 出库时必须输入价格
                    if not price_str:
                        messagebox.showerror("错误", "出库时必须输入售价！")
                        return
                    price = float(price_str)
                
                if price is not None and price < 0:
                    messagebox.showerror("错误", "价格不能为负数！")
                    return
                
                print(f"最终使用的价格: {price}")
            except ValueError as e:
                print(f"价格转换错误: {str(e)}")
                messagebox.showerror("错误", "请输入有效的价格！")
                return
            
            remark = self.remark_var.get()
            print(f"准备调用数据库操作: type={type}, quantity={quantity}, price={price}, remark={remark}")
            
            success, message = self.db.process_inventory(item_id, type, quantity, price, remark)
            print(f"数据库操作结果: success={success}, message={message}")
            
            if success:
                messagebox.showinfo("成功", message)
                self.clear_inventory_inputs()
                self.refresh_product_list()
            else:
                messagebox.showerror("错误", message)
                
        except ValueError as e:
            print(f"数量转换错误: {str(e)}")
            messagebox.showerror("错误", "请输入有效的数量！")
        except Exception as e:
            print(f"未预期的错误: {str(e)}")
            messagebox.showerror("错误", f"操作失败: {str(e)}")
            
    def clear_inventory_inputs(self):
        """清空出入库输入框"""
        self.inventory_quantity_var.set("")
        self.inventory_price_var.set("")
        self.remark_var.set("")
        self.clear_price_hint()  # 重置价格标签和提示
    
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
            # 格式化价格显示（带均价）
            price_display = f"{product[3]:.2f}"
            if product[4] != product[3]:  # 如果均价和当前价格不同
                price_display += f" ({product[4]:.1f})"
            
            values = (
                product[0],  # ID
                product[1],  # 名称
                product[2],  # 数量
                price_display,  # 价格(均价)
                product[5],  # 描述
                product[7].split('.')[0]  # 更新时间（去除毫秒）
            )
            
            # 如果均价高于当前价格，使用红色显示
            if product[4] > product[3]:
                self.tree.insert('', tk.END, values=values, tags=('high_avg_price',))
            else:
                self.tree.insert('', tk.END, values=values)
        
        # 设置标签样式
        self.tree.tag_configure('high_avg_price', foreground='red')
    
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
    
    def show_inventory_records(self):
        """显示出入库记录统计窗口"""
        InventoryRecordsWindow(self.root)

if __name__ == "__main__":
    root = tk.Tk()
    app = InventorySystem(root)
    root.mainloop() 