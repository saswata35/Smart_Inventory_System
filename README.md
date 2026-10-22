# 📦 Smart Inventory & Warehouse Tracking System (SIWTS)

Repo = https://github.com/saswata35/Smart_Inventory_System.git

A modular Python backend application designed to manage multi-warehouse inventories, execute ACID-compliant stock transactions, stream low-stock alerts, and automate executive auditing and reporting.

---

## 🚀 Key Features

* **Multi-Warehouse Management:** Seamlessly track and manage inventory levels across multiple warehouse locations.
* **ACID-Compliant Transactions:** Ensure database integrity and reliable stock movements with robust transaction handling.
* **Automated Low-Stock Alerts:** Stream and export low-stock notifications to CSV files for immediate action.
* **Executive Auditing & Reporting:** Automatically generate comprehensive JSON summaries and Markdown audit reports.

---

## 🛠️ Tech Stack

* **Language:** Python 3.x
* **Database & Management:** PostgreSQL, pgAdmin
* **Data Formats:** CSV, JSON, Markdown

---

## 📂 Project Structure

```text
Smart_Inventory_System/
├── exports/
│   ├── low_stock_alerts.csv
│   ├── inventory_summary.json
│   └── WAREHOUSE_AUDIT_REPORT.md
├── src/
│   ├── __init__.py
│   ├── database.py
│   ├── models.py
│   └── manager.py
├── main.py
├── README.md
└── requirements.txt


