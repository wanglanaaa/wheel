import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('inventory.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        """创建数据库表"""
        try:
            # 创建商品表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                price REAL NOT NULL DEFAULT 0,
                avg_price REAL NOT NULL DEFAULT 0,
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
                type TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL,
                cost_price REAL,
                remark TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
            ''')
            
            # 创建价格历史表
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
            ''')
            
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise Exception(f"创建数据库表失败: {str(e)}")
    
    def add_product(self, name, quantity, price, description=""):
        self.cursor.execute('''
        INSERT INTO products (name, quantity, price, avg_price, description)
        VALUES (?, ?, ?, ?, ?)
        ''', (name, quantity, price, price, description))
        
        product_id = self.cursor.lastrowid
        
        # 记录初始价格历史
        self.cursor.execute('''
        INSERT INTO price_history (product_id, price, quantity)
        VALUES (?, ?, ?)
        ''', (product_id, price, quantity))
        
        self.conn.commit()
        return product_id
    
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
            # 记录新价格历史
            self.cursor.execute('''
            INSERT INTO price_history (product_id, price, quantity)
            VALUES (?, ?, ?)
            ''', (id, price, quantity if quantity is not None else self.get_product(id)[2]))
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
    
    def calculate_average_price(self, product_id):
        """计算商品的加权平均价格"""
        try:
            self.cursor.execute('''
            SELECT SUM(price * quantity) / SUM(quantity) as avg_price
            FROM price_history
            WHERE product_id = ?
            ''', (product_id,))
            result = self.cursor.fetchone()
            return round(result[0], 1) if result[0] is not None else 0.0
        except Exception as e:
            print(f"计算平均价格失败: {str(e)}")
            return 0.0
    
    def process_inventory(self, product_id, type, quantity, price=None, remark=""):
        """处理出入库操作"""
        try:
            # 获取当前商品
            product = self.get_product(product_id)
            if not product:
                return False, "商品不存在"
            
            current_quantity = product[2]  # quantity在第三列
            current_price = product[3]     # price在第四列
            current_avg_price = product[4]  # avg_price在第五列
            
            # 计算新数量
            if type == 'in':
                new_quantity = current_quantity + quantity
                # 如果没有指定入库价格，使用当前价格
                if price is None:
                    price = current_price
                
                # 记录新价格历史
                self.cursor.execute('''
                INSERT INTO price_history (product_id, price, quantity)
                VALUES (?, ?, ?)
                ''', (product_id, price, quantity))
                
                # 更新平均价格
                avg_price = self.calculate_average_price(product_id)
                
                # 更新商品信息
                self.cursor.execute('''
                UPDATE products 
                SET quantity = ?, 
                    price = ?,
                    avg_price = ?,
                    updated_at = datetime('now', 'localtime')
                WHERE id = ?
                ''', (new_quantity, price, avg_price, product_id))
                
            elif type == 'out':
                new_quantity = current_quantity - quantity
                if new_quantity < 0:
                    return False, "库存不足"
                
                if price is None:
                    return False, "出库时必须指定售价"
                
                # 更新商品数量
                self.cursor.execute('''
                UPDATE products 
                SET quantity = ?,
                    updated_at = datetime('now', 'localtime')
                WHERE id = ?
                ''', (new_quantity, product_id))
            else:
                return False, "无效的操作类型"
            
            # 记录出入库信息
            self.cursor.execute('''
            INSERT INTO inventory_records 
                (product_id, type, quantity, price, cost_price, remark, created_at)
            VALUES 
                (?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
            ''', (
                product_id,
                type,
                quantity,
                price,
                current_avg_price if type == 'out' else None,
                remark
            ))
            
            self.conn.commit()
            return True, "操作成功"
            
        except Exception as e:
            self.conn.rollback()
            return False, f"操作失败: {str(e)}"
    
    def get_inventory_records(self, product_id=None):
        """获取出入库记录"""
        if product_id:
            self.cursor.execute("""
            SELECT r.*, p.name, datetime(r.created_at, 'localtime') as local_time
            FROM inventory_records r
            JOIN products p ON r.product_id = p.id
            WHERE r.product_id = ?
            ORDER BY r.created_at DESC
            """, (product_id,))
        else:
            self.cursor.execute("""
            SELECT r.*, p.name, datetime(r.created_at, 'localtime') as local_time
            FROM inventory_records r
            JOIN products p ON r.product_id = p.id
            ORDER BY r.created_at DESC
            """)
        return self.cursor.fetchall()
    
    def get_all_products(self):
        self.cursor.execute("""
        SELECT id, name, quantity, price, avg_price, description, 
               datetime(created_at, 'localtime') as created_at,
               datetime(updated_at, 'localtime') as updated_at
        FROM products 
        ORDER BY name
        """)
        return self.cursor.fetchall()
    
    def get_product(self, id):
        self.cursor.execute("""
        SELECT id, name, quantity, price, avg_price, description,
               datetime(created_at, 'localtime') as created_at,
               datetime(updated_at, 'localtime') as updated_at
        FROM products 
        WHERE id = ?
        """, (id,))
        return self.cursor.fetchone()
    
    def search_products(self, keyword):
        self.cursor.execute("""
        SELECT id, name, quantity, price, avg_price, description,
               datetime(created_at, 'localtime') as created_at,
               datetime(updated_at, 'localtime') as updated_at
        FROM products 
        WHERE name LIKE ? OR description LIKE ?
        ORDER BY name
        """, (f"%{keyword}%", f"%{keyword}%"))
        return self.cursor.fetchall()
    
    def delete_product(self, id):
        self.cursor.execute("DELETE FROM products WHERE id = ?", (id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def __del__(self):
        self.conn.close() 