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
from models.supplier import Supplier
from models.customer import Customer
from models.partner import Partner
from models.purchase import Purchase, PurchaseItem
from models.stock import StockMovement
from models.cash_bank import Account, CashBankTransaction


class Phase2TestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db_path = os.path.join(base_dir, "test_phase2.db")
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

    def test_01_product_crud(self):
        """Test Product Master add, list, duplicate prevention, and edit."""
        # Add Product
        response = self.client.post("/products", data={
            "action": "add",
            "code": "TST-01",
            "name": "Test Plate",
            "category": "Crockery",
            "unit": "Pcs",
            "cost_price": "120.00",
            "sale_price": "180.00",
            "opening_stock": "50",
            "min_stock_alert": "10",
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            prod = Product.query.filter_by(code="TST-01").first()
            self.assertIsNotNone(prod)
            self.assertEqual(prod.name, "Test Plate")
            self.assertEqual(prod.current_stock, 50.0)
            self.assertEqual(prod.cost_price, 120.0)

        # Duplicate Code Prevention
        dup_res = self.client.post("/products", data={
            "action": "add",
            "code": "TST-01",
            "name": "Duplicate Item",
        }, follow_redirects=True)
        self.assertIn("already exists", dup_res.data.decode("utf-8"))

    def test_02_supplier_crud(self):
        """Test Supplier Master add and query."""
        response = self.client.post("/suppliers", data={
            "action": "add",
            "name": "Sheikh Crockery Supplier",
            "phone": "0300-1122334",
            "city": "Gujranwala",
            "opening_balance": "5000.00",
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            sup = Supplier.query.filter_by(name="Sheikh Crockery Supplier").first()
            self.assertIsNotNone(sup)
            self.assertEqual(sup.city, "Gujranwala")
            self.assertEqual(sup.current_balance, 5000.0)

    def test_03_customer_crud(self):
        """Test Customer Master add and query."""
        response = self.client.post("/customers", data={
            "action": "add",
            "name": "Bismillah General Store",
            "phone": "0321-9988776",
            "city": "Lahore",
            "opening_balance": "2500.00",
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            cust = Customer.query.filter_by(name="Bismillah General Store").first()
            self.assertIsNotNone(cust)
            self.assertEqual(cust.city, "Lahore")
            self.assertEqual(cust.current_balance, 2500.0)

    def test_04_purchase_transaction_accounting_connection(self):
        """
        Verify complete relational accounting connection:
        Purchase -> Stock Increase -> Supplier Payable Balance -> Cash Account Deduction.
        """
        with self.app.app_context():
            # Prepare pre-conditions
            sup = Supplier(name="Master Ceramics", opening_balance=0.0, current_balance=0.0)
            prod = Product(code="BWL-01", name="Soup Bowl", current_stock=20.0, cost_price=80.0)
            cash = Account.query.filter_by(account_type="Cash").first()
            cash.balance = 10000.0  # Initial cash 10,000

            db.session.add_all([sup, prod])
            db.session.commit()

            sup_id = sup.id
            prod_id = prod.id
            cash_id = cash.id

        # Record a Purchase:
        # 30 bowls @ 100 PKR = 3,000 PKR Total
        # Paid: 1,000 PKR Cash
        # Balance: 2,000 PKR Payable
        response = self.client.post("/purchases/new", data={
            "bill_no": "BILL-TEST-99",
            "date": "2026-10-01",
            "supplier_id": sup_id,
            "product_id[]": [prod_id],
            "quantity[]": ["30"],
            "unit[]": ["Pcs"],
            "rate[]": ["100"],
            "paid_amount": "1000.00",
            "account_id": cash_id,
            "notes": "Testing accounting connections",
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            # 1. Check Purchase Record
            purchase = Purchase.query.filter_by(bill_no="BILL-TEST-99").first()
            self.assertIsNotNone(purchase)
            self.assertEqual(purchase.total_amount, 3000.0)
            self.assertEqual(purchase.paid_amount, 1000.0)
            self.assertEqual(purchase.balance_amount, 2000.0)
            self.assertEqual(purchase.payment_status, "Partial")

            # 2. Check Stock Connection
            updated_prod = db.session.get(Product, prod_id)
            self.assertEqual(updated_prod.current_stock, 50.0, "Stock should increase from 20 to 50!")
            self.assertEqual(updated_prod.cost_price, 100.0, "Cost rate should update to 100!")

            # 3. Check Stock Movement Log
            movement = StockMovement.query.filter_by(reference_id=purchase.id).first()
            self.assertIsNotNone(movement)
            self.assertEqual(movement.movement_type, "IN")
            self.assertEqual(movement.quantity, 30.0)

            # 4. Check Supplier Payable Connection
            updated_sup = db.session.get(Supplier, sup_id)
            self.assertEqual(updated_sup.current_balance, 2000.0, "Supplier payable balance should increase by 2,000!")

            # 5. Check Cash Account Deduction
            updated_cash = db.session.get(Account, cash_id)
            self.assertEqual(updated_cash.balance, 9000.0, "Cash balance should reduce from 10,000 to 9,000!")

            # 6. Check Cash Transaction Log
            cash_txn = CashBankTransaction.query.filter_by(reference_id=purchase.id).first()
            self.assertIsNotNone(cash_txn)
            self.assertEqual(cash_txn.amount, 1000.0)
            self.assertEqual(cash_txn.transaction_type, "Supplier Payment")

    def test_05_stock_register_view(self):
        """Verify stock register displays products and valuation."""
        response = self.client.get("/stock")
        self.assertEqual(response.status_code, 200)
        content = response.data.decode("utf-8")
        self.assertIn("Automatic Stock Register", content)
        self.assertIn("BWL-01", content)
        self.assertIn("Soup Bowl", content)

    def test_06_supplier_ledger_view(self):
        """Verify supplier ledger shows purchase and balance."""
        response = self.client.get("/supplier-ledger")
        self.assertEqual(response.status_code, 200)
        content = response.data.decode("utf-8")
        self.assertIn("Supplier Payable Ledger", content)
        self.assertIn("BILL-TEST-99", content)
        self.assertIn("Master Ceramics", content)

    def test_07_excel_import_preview_and_execution(self):
        """Test Excel import tool preview and execution with original workbook."""
        # GET preview
        res = self.client.get("/import-excel")
        self.assertEqual(res.status_code, 200)
        content = res.data.decode("utf-8")
        self.assertIn("Original Excel Workbook Source", content)

        # POST execute import
        import_res = self.client.post("/import-excel", data={"action": "execute_import"}, follow_redirects=True)
        self.assertEqual(import_res.status_code, 200)

        with self.app.app_context():
            # Check products imported from Excel
            pl10 = Product.query.filter_by(code="PL-10").first()
            self.assertIsNotNone(pl10, "PL-10 should be imported from Excel!")
            self.assertIn("Plate 10 Inch", pl10.name)
            self.assertEqual(pl10.cost_price, 250.0)

            # Check purchase imported from Excel
            r001 = Purchase.query.filter_by(bill_no="R-001").first()
            self.assertIsNotNone(r001, "R-001 purchase should be imported from Excel!")
            self.assertEqual(r001.total_amount, 6750.0)
            self.assertEqual(r001.paid_amount, 5000.0)
            self.assertEqual(r001.balance_amount, 1750.0)


if __name__ == "__main__":
    unittest.main()
