"""
Smart Inventory & Warehouse Tracking System (SIWTS) Package
"""

from src.database import WarehouseDB
from src.manager import InventoryManager, InventoryError, InsufficientStockError

__version__ = "1.0.0"
__all__ = [
    "WarehouseDB",
    "InventoryManager",
    "InventoryError",
    "InsufficientStockError"
]