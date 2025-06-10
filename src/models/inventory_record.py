"""
出入库记录模型
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Literal

@dataclass
class InventoryRecord:
    """出入库记录类"""
    id: Optional[int]
    product_id: int
    product_name: str
    type: Literal['in', 'out']
    quantity: int
    price: Optional[float]
    cost_price: Optional[float]
    remark: str
    created_at: datetime

    @property
    def type_text(self) -> str:
        """操作类型文本"""
        return "入库" if self.type == "in" else "出库"

    @property
    def total_price(self) -> float:
        """总价"""
        if self.price is None or self.quantity is None:
            return 0.0
        return self.price * self.quantity

    @property
    def profit(self) -> Optional[float]:
        """毛利（仅出库时计算）"""
        if self.type == 'out' and all(x is not None for x in [self.price, self.cost_price, self.quantity]):
            return (self.price - self.cost_price) * self.quantity
        return None

    def to_dict(self) -> dict:
        """转换为字典，用于导出"""
        return {
            '时间': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            '商品名称': self.product_name,
            '类型': self.type_text,
            '数量': self.quantity,
            '单价': f"{self.price:.2f}" if self.price is not None else "-",
            '成本价': f"{self.cost_price:.2f}" if self.cost_price is not None else "-",
            '总价': f"{self.total_price:.2f}" if self.total_price != 0 else "-",
            '毛利': f"{self.profit:.2f}" if self.profit is not None else "-",
            '备注': self.remark or "-"
        } 