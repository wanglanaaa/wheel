"""
商品模型
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Product:
    """商品类"""
    id: Optional[int]
    name: str
    quantity: int
    price: float
    avg_price: float
    description: str
    created_at: datetime
    updated_at: datetime

    @property
    def price_display(self) -> str:
        """价格显示（带均价）"""
        price_str = f"{self.price:.2f}"
        if self.avg_price != self.price:
            price_str += f" ({self.avg_price:.1f})"
        return price_str

    @property
    def has_high_avg_price(self) -> bool:
        """判断是否均价高于当前价格"""
        return self.avg_price > self.price 