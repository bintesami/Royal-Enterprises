import os
import sys
import unittest

# Ensure crockery_app is first in Python path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
app_dir = os.path.join(base_dir, "crockery_app")
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from app import create_app, db
from models.user import User
from models.product import Product
from models.customer import Customer
from models.sale import Sale, SaleItem
from models.stock import StockMovement
from models.cash_bank import Account, CashBankTransaction


class Phase34TestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db_path = os.path.join(base_dir, "test_phase34.db")
        if os.path.exists(cls.test_db_path):
            try:
                os.remove(cls.test_db_path)
            except Exception:
                pass
        cls.app = create_app({
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{cls.test_db_path}",
        })
        cls.client = cls.app.test_client()

        # Login admin
        cls.client.post("/login", data={"username": "admin", "password": "admin123"})

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_db_path):
            try:
                os.remove(cls.test_db_path)
            except Exception:
                pass

    def test_01_sales_transaction_and_accounting_connections(self):
        """
        Verify:
        Sale -> Stock Decrease (StockMovement OUT) -> Customer Ledger (Receivable) -> COGS & Gross Profit.
        """
        with self.app.app_context():
            cust = Customer(name="Rahim Store,wapda town", opening_balance=0.0, current_balance=0.0)
            prod = Product(code="RK-02", name="Racks 2 Khana", current_stock=10.0, cost_price=1350.0, sale_price=1800.0)
            db.session.add_all([cust, prod])
            db.session.commit()

            cust_id = cust.id
            prod_id = prod.id

        # Record Sale: 6 Units @ 1,800 = 10,800 Total, Cost = 8,100, Profit = 2,700, Received = 0
        response = self.client.post("/sales/new", data={
            "invoice_no": "R.001",
            "date": "2026-08-17",
            "customer_id": cust_id,
            "product_id[]": [prod_id],
            "quantity[]": ["6"],
            "unit[]": ["PCC"],
            "cost_rate[]": ["1350"],
            "sale_rate[]": ["1800"],
            "received_amount": "0.00",
            "notes": "Original Excel Test Sale",
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            # 1. Verify Sale Record & Calculations
            sale = Sale.query.filter_by(invoice_no="R.001").first()
            self.assertIsNotNone(sale)
            self.assertEqual(sale.total_sale, 10800.0)
            self.assertEqual(sale.total_cost, 8100.0)
            self.assertEqual(sale.gross_profit, 2700.0)
            self.assertEqual(sale.received_amount, 0.0)
            self.assertEqual(sale.balance_amount, 10800.0)
            self.assertEqual(sale.payment_status, "Unpaid")

            # 2. Verify Stock Deduction
            updated_prod = db.session.get(Product, prod_id)
            self.assertEqual(updated_prod.current_stock, 4.0, "Stock should decrease from 10 to 4!")

            # 3. Verify Stock Movement OUT
            mov = StockMovement.query.filter_by(reference_id=sale.id, movement_type="OUT").first()
            self.assertIsNotNone(mov)
            self.assertEqual(mov.quantity, 6.0)
            self.assertEqual(mov.unit_cost, 1350.0)

            # 4. Verify Customer Receivable Balance
            updated_cust = db.session.get(Customer, cust_id)
            self.assertEqual(updated_cust.current_balance, 10800.0, "Customer receivable should increase by 10,800!")

    def test_02_sales_with_cash_receipt(self):
        """Verify sale with cash receipt increases cash account balance and logs receipt transaction."""
        with self.app.app_context():
            cust = Customer.query.filter_by(name="Rahim Store,wapda town").first()
            prod = Product.query.filter_by(code="RK-02").first()
            cash = Account.query.filter_by(account_type="Cash").first()
            cash.balance = 50000.0
            db.session.commit()

            cust_id = cust.id
            prod_id = prod.id
            cash_id = cash.id

        # Sell 2 units @ 1800 = 3,600 Total, Received: 2,000, Balance: 1,600
        response = self.client.post("/sales/new", data={
            "invoice_no": "R.002",
            "date": "2026-08-18",
            "customer_id": cust_id,
            "product_id[]": [prod_id],
            "quantity[]": ["2"],
            "unit[]": ["PCC"],
            "cost_rate[]": ["1350"],
            "sale_rate[]": ["1800"],
            "received_amount": "2000.00",
            "account_id": cash_id,
            "notes": "Sale with partial payment",
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            sale = Sale.query.filter_by(invoice_no="R.002").first()
            self.assertIsNotNone(sale)
            self.assertEqual(sale.total_sale, 3600.0)
            self.assertEqual(sale.received_amount, 2000.0)
            self.assertEqual(sale.balance_amount, 1600.0)
            self.assertEqual(sale.payment_status, "Partial")

            # Cash account should increase from 50,000 to 52,000
            updated_cash = db.session.get(Account, cash_id)
            self.assertEqual(updated_cash.balance, 52000.0)

            # Cash transaction logged
            c_txn = CashBankTransaction.query.filter_by(reference_id=sale.id).first()
            self.assertIsNotNone(c_txn)
            self.assertEqual(c_txn.amount, 2000.0)
            self.assertEqual(c_txn.transaction_type, "Customer Receipt")

            # Customer balance should increase from 10,800 by 1,600 -> 12,400
            updated_cust = db.session.get(Customer, cust_id)
            self.assertEqual(updated_cust.current_balance, 12400.0)

            # Product stock drops from 4 to 2
            updated_prod = db.session.get(Product, prod_id)
            self.assertEqual(updated_prod.current_stock, 2.0)

    def test_03_sales_register_view(self):
        """Verify sales register view lists invoices and summary metrics."""
        response = self.client.get("/sales")
        self.assertEqual(response.status_code, 200)
        content = response.data.decode("utf-8")
        self.assertIn("Sales Register", content)
        self.assertIn("R.001", content)
        self.assertIn("R.002", content)
        self.assertIn("Rahim Store", content)

    def test_04_sales_invoice_view(self):
        """Verify printable sales invoice view."""
        with self.app.app_context():
            sale = Sale.query.filter_by(invoice_no="R.001").first()
            sale_id = sale.id

        response = self.client.get(f"/sales/{sale_id}")
        self.assertEqual(response.status_code, 200)
        content = response.data.decode("utf-8")
        self.assertIn("INVOICE # R.001", content)
        self.assertIn("Rahim Store", content)
        self.assertIn("10,800.00", content)

    def test_05_customer_ledger_view(self):
        """Verify customer ledger displays sales and receivable balances."""
        response = self.client.get("/customer-ledger")
        self.assertEqual(response.status_code, 200)
        content = response.data.decode("utf-8")
        self.assertIn("Customer Receivable Ledger", content)
        self.assertIn("R.001", content)
        self.assertIn("Rahim Store", content)

    def test_06_excel_sales_importer(self):
        """Verify importer imports Sales sheet from original Excel workbook."""
        # Execute import
        res = self.client.post("/import-excel", data={"action": "execute_import"}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        with self.app.app_context():
            # Check customer created from Excel Sales
            rahim = Customer.query.filter(Customer.name.ilike("%Rahim Store%")).first()
            self.assertIsNotNone(rahim, "Customer from Excel sales should be present!")

            # Check invoice from Excel Sales
            inv = Sale.query.filter_by(invoice_no="R.001").first()
            self.assertIsNotNone(inv)
            self.assertEqual(inv.total_sale, 10800.0)
            self.assertEqual(inv.gross_profit, 2700.0)


if __name__ == "__main__":
    unittest.main()
