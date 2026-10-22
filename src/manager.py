import csv
import json
import os
from datetime import datetime
from typing import Dict, Any, Generator
from src.database import WarehouseDB

class InventoryError(Exception):
    """Base exception for inventory errors."""
    pass

class InsufficientStockError(InventoryError):
    """Raised when attempting to remove more stock than available."""
    pass

class InventoryManager:
    """Core class handling warehouse stock, transactions, and reporting."""

    def __init__(self, db: WarehouseDB):
        self.db = db

    def add_warehouse(self, name: str, city: str) -> None:
        with self.db.get_connection() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO warehouses (name, city) VALUES (?, ?)",
                (name.strip(), city.strip())
            )
            conn.commit()

    def add_product(self, sku: str, name: str, category: str, unit_price: float) -> None:
        with self.db.get_connection() as conn:
            conn.execute(
                """INSERT OR IGNORE INTO products (sku, name, category, unit_price) 
                   VALUES (?, ?, ?, ?)""",
                (sku.upper().strip(), name.strip(), category.strip(), unit_price)
            )
            conn.commit()

    def set_stock(self, warehouse_name: str, sku: str, quantity: int, min_threshold: int = 10) -> None:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT warehouse_id FROM warehouses WHERE name = ?", (warehouse_name,))
            wh = cursor.fetchone()
            cursor.execute("SELECT product_id FROM products WHERE sku = ?", (sku.upper(),))
            prod = cursor.fetchone()

            if not wh or not prod:
                raise InventoryError("Warehouse or Product SKU not found.")

            cursor.execute(
                """INSERT INTO inventory (warehouse_id, product_id, quantity, min_threshold)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(warehouse_id, product_id) 
                   DO UPDATE SET quantity = ?, min_threshold = ?""",
                (wh["warehouse_id"], prod["product_id"], quantity, min_threshold, quantity, min_threshold)
            )
            conn.commit()

    def process_transaction(self, warehouse_name: str, sku: str, qty: int, tx_type: str) -> None:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT warehouse_id FROM warehouses WHERE name = ?", (warehouse_name,))
            wh = cursor.fetchone()
            cursor.execute("SELECT product_id FROM products WHERE sku = ?", (sku.upper(),))
            prod = cursor.fetchone()

            if not wh or not prod:
                raise InventoryError("Invalid warehouse or SKU.")

            wh_id, prod_id = wh["warehouse_id"], prod["product_id"]

            if tx_type == "DISPATCH":
                cursor.execute(
                    "SELECT quantity FROM inventory WHERE warehouse_id = ? AND product_id = ?",
                    (wh_id, prod_id)
                )
                row = cursor.fetchone()
                current_qty = row["quantity"] if row else 0
                if current_qty < qty:
                    raise InsufficientStockError(f"Stock deficit for SKU {sku}. Available: {current_qty}")
                
                change = -qty
                new_qty = current_qty - qty
            else:
                change = qty
                cursor.execute(
                    "SELECT quantity FROM inventory WHERE warehouse_id = ? AND product_id = ?",
                    (wh_id, prod_id)
                )
                row = cursor.fetchone()
                new_qty = (row["quantity"] if row else 0) + qty

            cursor.execute(
                """UPDATE inventory SET quantity = ? WHERE warehouse_id = ? AND product_id = ?""",
                (new_qty, wh_id, prod_id)
            )
            cursor.execute(
                """INSERT INTO stock_transactions (product_id, warehouse_id, change_qty, tx_type, timestamp)
                   VALUES (?, ?, ?, ?, ?)""",
                (prod_id, wh_id, change, tx_type, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            conn.commit()

    def stream_low_stock(self) -> Generator[Dict[str, Any], None, None]:
        with self.db.get_connection() as conn:
            query = """
                SELECT w.name as warehouse, p.sku, p.name as product, i.quantity, i.min_threshold
                FROM inventory i
                JOIN warehouses w ON i.warehouse_id = w.warehouse_id
                JOIN products p ON i.product_id = p.product_id
                WHERE i.quantity <= i.min_threshold
            """
            for row in conn.execute(query):
                yield dict(row)

    def export_low_stock_csv(self, filename: str = "exports/low_stock_alerts.csv") -> None:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Warehouse", "SKU", "Product Name", "Current Qty", "Min Threshold"])
            for item in self.stream_low_stock():
                writer.writerow([item["warehouse"], item["sku"], item["product"], item["quantity"], item["min_threshold"]])
        print(f"[CSV] Low stock alerts exported to {filename}")

    def export_inventory_summary_json(self, filename: str = "exports/inventory_summary.json") -> None:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with self.db.get_connection() as conn:
            query = """
                SELECT w.name as warehouse, SUM(i.quantity) as total_items, 
                       ROUND(SUM(i.quantity * p.unit_price), 2) as total_inventory_value
                FROM inventory i
                JOIN warehouses w ON i.warehouse_id = w.warehouse_id
                JOIN products p ON i.product_id = p.product_id
                GROUP BY w.warehouse_id
            """
            summary = [dict(row) for row in conn.execute(query)]

        data = {"generated_at": datetime.now().isoformat(), "warehouses": summary}
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"[JSON] Inventory summary saved to {filename}")

    def generate_markdown_audit_report(self, filename: str = "exports/WAREHOUSE_AUDIT_REPORT.md") -> None:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with self.db.get_connection() as conn:
            total_skus = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
            total_warehouses = conn.execute("SELECT COUNT(*) FROM warehouses").fetchone()[0]
            total_units = conn.execute("SELECT SUM(quantity) FROM inventory").fetchone()[0] or 0

            details_query = """
                SELECT w.name as warehouse, p.sku, p.name as product, p.category, i.quantity, p.unit_price
                FROM inventory i
                JOIN warehouses w ON i.warehouse_id = w.warehouse_id
                JOIN products p ON i.product_id = p.product_id
            """
            items = conn.execute(details_query).fetchall()

        report = [
            "# 📦 Smart Warehouse & Inventory Audit Report",
            f"Generated on: **{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**\n",
            "## 🌐 System Overview",
            f"* **Total Registered Warehouses:** {total_warehouses}",
            f"* **Total Unique Product SKUs:** {total_skus}",
            f"* **Total Stock Units Across Facilities:** {total_units:,}\n",
            "---",
            "## 📋 Comprehensive Stock Register",
            "| Warehouse | SKU | Product Name | Category | Qty | Unit Price ($) |",
            "|-----------|-----|--------------|----------|-----|----------------|"
        ]

        for row in items:
            report.append(f"| {row['warehouse']} | {row['sku']} | {row['product']} | {row['category']} | {row['quantity']} | ${row['unit_price']:,.2f} |")

        report.append("\n---\n*_Report auto-generated by Smart Inventory & Warehouse Tracking System (SIWTS)._*")

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(report))
        print(f"[Markdown] Audit report successfully compiled at {filename}")



