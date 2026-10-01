# Crockery Wholesale Partnership Accounting & Inventory System

A production-grade Python Flask and SQLite accounting and inventory management system designed specifically for crockery wholesale partnerships. Built strictly to match and enhance the 11 original modules of wholesale business operations with true double-entry bookkeeping, perpetual inventory valuation, and partner equity tracking.

---

## 🌟 Key Features & Modules

1. **Dashboard (/)**: Real-time business KPIs (Sales, Gross/Net Profit, Cash & Bank balances, Receivables, Payables, Capital Pool).
2. **Partners Capital (/partners)**: Partner equity management, 50/50 profit sharing, capital injection/withdrawal vouchers, and running statements.
3. **Purchases (/purchases)**: Wholesale purchase invoice entry, cost calculations, real-time stock addition, and supplier payable updates.
4. **Sales (/sales)**: Wholesale invoicing, line-item COGS computation, automatic stock reduction, customer receivable tracking, and printable bills.
5. **Customer Ledger (/ledgers/customer)**: Filterable running customer ledger showing debit, credit, and running balance with print support.
6. **Supplier Ledger (/ledgers/supplier)**: Filterable running supplier ledger tracking purchases and payments.
7. **Expenses (/expenses)**: Operating overheads register (Rent, Electricity, Labor, Freight, etc.) with Cash/Bank integration and printable payment slips.
8. **Stock (/stock)**: Inventory status at cost, low-stock warnings, chronological stock movement ledger (/stock/ledger), and audit/breakage adjustments (/stock/adjustments/new).
9. **Cash & Bank Book (/cash-bank)**: Unified double-entry cash and bank book, customer receipt vouchers, supplier payment vouchers, and account transfers.
10. **Partner Drawings (/partner-drawings)**: Personal withdrawal vouchers and register matching wholesale partnership requirements.
11. **Monthly Profit & 50/50 Sharing (/monthly-profit)**: Monthly revenue, actual COGS, gross profit, operating overheads, net profit, and 1-click 50/50 profit distribution.

### Financial Reports & Utilities
- **Double-Entry Trial Balance (/reports/trial-balance)**: Instant verification that $\sum \text{Debit} = \sum \text{Credit}$.
- **Profit & Loss Statement (/reports/profit-loss)**: Formal income statement.
- **Balance Sheet (/reports/balance-sheet)**: Balance sheet ensuring $\text{Assets} = \text{Liabilities} + \text{Equity}$.
- **System Settings (/settings)**: Configurable business profile (name, address, phone, currency, invoice footer).
- **1-Click Database Backup (/settings/backup)**: Downloads clean, timestamped SQLite snapshot (crockery_backup_YYYYMMDD_HHMMSS.db).
- **Excel Importer (/import-excel)**: One-click import for legacy Excel data.

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+
- pip

### 1. Installation
`ash
git clone <your-repository-url>
cd Royal Enterprises
pip install -r crockery_app/requirements.txt
`

### 2. Run the Application
`ash
python run.py
`
Access the application at: http://127.0.0.1:5000

### 3. Default Credentials
- **Username:** dmin
- **Password:** dmin123

---

## 🧪 Automated Testing
Run the complete automated test suite (54 unit and integration tests):
`ash
python -m unittest discover tests
`
