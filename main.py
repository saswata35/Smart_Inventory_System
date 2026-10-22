from src.database import WarehouseDB
from src.manager import InventoryManager

if __name__ == "__main__":
    db = WarehouseDB("data/warehouse_data.db")
    manager = InventoryManager(db)

    # 1. Setup Warehouses & Products
    manager.add_warehouse("Central Hub", "Kolkata")
    manager.add_warehouse("West Facility", "Mumbai")

    manager.add_product("LAP-001", "Dell Latitude 5420", "Electronics", 750.00)
    manager.add_product("MOU-002", "Logitech Wireless Mouse", "Accessories", 25.50)
    manager.add_product("KEY-003", "Mechanical RGB Keyboard", "Accessories", 65.00)

    # 2. Set Initial Stock Levels
    manager.set_stock("Central Hub", "LAP-001", 15, min_threshold=5)
    manager.set_stock("Central Hub", "MOU-002", 8, min_threshold=10) # Triggers low stock alert
    manager.set_stock("West Facility", "KEY-003", 25, min_threshold=10)

    # 3. Simulate Stock Transactions
    print("\nProcessing transactions...")
    manager.process_transaction("Central Hub", "LAP-001", 3, "DISPATCH")
    manager.process_transaction("West Facility", "KEY-003", 10, "RESTOCK")

    # 4. Export Files (CSV, JSON, Markdown)
    manager.export_low_stock_csv("exports/low_stock_alerts.csv")
    manager.export_inventory_summary_json("exports/inventory_summary.json")
    manager.generate_markdown_audit_report("exports/WAREHOUSE_AUDIT_REPORT.md")
    print("\nAll inventory operations completed successfully!")