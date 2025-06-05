import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('inventory.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        # 创建商品表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 创建出入库记录表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            type TEXT NOT NULL,  -- 'in' for 入库, 'out' for 出库
            quantity INTEGER NOT NULL,
            remark TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
        ''')
        self.conn.commit()
    
    def add_product(self, name, quantity, price, description=""):
        self.cursor.execute('''
        INSERT INTO products (name, quantity, price, description)
        VALUES (?, ?, ?, ?)
        ''', (name, quantity, price, description))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def update_product(self, id, name=None, quantity=None, price=None, description=None):
        updates = []
        values = []
        if name is not None:
            updates.append("name = ?")
            values.append(name)
        if quantity is not None:
            updates.append("quantity = ?")
            values.append(quantity)
        if price is not None:
            updates.append("price = ?")
            values.append(price)
        if description is not None:
            updates.append("description = ?")
            values.append(description)
        
        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            query = f"UPDATE products SET {', '.join(updates)} WHERE id = ?"
            values.append(id)
            self.cursor.execute(query, values)
            self.conn.commit()
            return True
        return False
    
    def delete_product(self, id):
        self.cursor.execute("DELETE FROM products WHERE id = ?", (id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def get_all_products(self):
        self.cursor.execute("SELECT * FROM products ORDER BY name")
        return self.cursor.fetchall()
    
    def get_product(self, id):
        self.cursor.execute("SELECT * FROM products WHERE id = ?", (id,))
        return self.cursor.fetchone()
    
    def search_products(self, keyword):
        self.cursor.execute("""
        SELECT * FROM products 
        WHERE name LIKE ? OR description LIKE ?
        ORDER BY name
        """, (f"%{keyword}%", f"%{keyword}%"))
        return self.cursor.fetchall()
    
    def process_inventory(self, product_id, type, quantity, remark=""):
        """处理出入库操作"""
        # 获取当前商品
        product = self.get_product(product_id)
        if not product:
            return False, "商品不存在"
        
        current_quantity = product[2]  # quantity在第三列
        
        # 计算新数量
        if type == 'in':
            new_quantity = current_quantity + quantity
        elif type == 'out':
            new_quantity = current_quantity - quantity
            if new_quantity < 0:
                return False, "库存不足"
        else:
            return False, "无效的操作类型"
        
        # 更新商品数量
        self.update_product(product_id, quantity=new_quantity)
        
        # 记录出入库信息
        self.cursor.execute('''
        INSERT INTO inventory_records (product_id, type, quantity, remark)
        VALUES (?, ?, ?, ?)
        ''', (product_id, type, quantity, remark))
        self.conn.commit()
        
        return True, "操作成功"
    
    def get_inventory_records(self, product_id=None):
        """获取出入库记录"""
        if product_id:
            self.cursor.execute("""
            SELECT r.*, p.name 
            FROM inventory_records r
            JOIN products p ON r.product_id = p.id
            WHERE r.product_id = ?
            ORDER BY r.created_at DESC
            """, (product_id,))
        else:
            self.cursor.execute("""
            SELECT r.*, p.name 
            FROM inventory_records r
            JOIN products p ON r.product_id = p.id
            ORDER BY r.created_at DESC
            """)
        return self.cursor.fetchall()
    
    def __del__(self):
        self.conn.close() 