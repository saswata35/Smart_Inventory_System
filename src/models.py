from dataclasses import dataclass

@dataclass
class Warehouse:
    warehouse_id: int
    name: str
    city: str

@dataclass
class Product:
    product_id: int
    sku: str
    name: str
    category: str
    unit_price: float

@dataclass
class InventoryItem:
    warehouse_id: int
    product_id: int
    quantity: int
    min_threshold: int