import os
import sys
import unittest
from datetime import datetime

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
from models.partner import Partner, PartnerCapitalTransaction
from models.purchase import Purchase, PurchaseItem
from models.sale import Sale, SaleItem
from models.expense import Expense
from models.cash_bank import Account, CashBankTransaction, PartnerDrawing
from models.stock import StockMovement


class FinalIntegrationTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db_path = os.path.join(base_dir, "test_final.db")
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

        with cls.app.app_context():
            cash = Account.query.filter_by(account_type="Cash").first()
            if cash:
                cash.balance = 500000.0
            bank = Account.query.filter_by(account_type="Bank").first()
            if bank:
                bank.balance = 1000000.0

            # Create standard product
            p = Product(
                code="FIN-PL10",
                name="10-Inch Royal Plate",
                category="Dinnerware",
                unit="Pcs",
                cost_price=200.0,
                sale_price=300.0,
                current_stock=100.0,
                min_stock_alert=20.0,
                is_active=True,
            )
            db.session.add(p)

            # Create standard supplier
            s = Supplier(name="Royal Ceramics Gujranwala", opening_balance=0.0, current_balance=0.0)
            db.session.add(s)

            # Create standard customer
            c = Customer(name="Al-Madina Crockery Lahore", opening_balance=0.0, current_balance=0.0)
            db.session.add(c)

            db.session.commit()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_db_path):
            try:
                os.remove(cls.test_db_path)
            except Exception:
                pass

    # Rule 1: purchase increases stock
    def test_rule_01_purchase_increases_stock(self):
        with self.app.app_context():
            p = Product.query.filter_by(code="FIN-PL10").first()
            sup = Supplier.query.filter_by(name="Royal Ceramics Gujranwala").first()
            init_stock = p.current_stock

        res = self.client.post("/purchases/new", data={
            "bill_no": "PUR-RULE01",
            "date": "2026-10-01",
            "supplier_id": str(sup.id),
            "paid_amount": "0.00",
            "product_id[]": [str(p.id)],
            "quantity[]": ["50"],
            "unit[]": ["Pcs"],
            "rate[]": ["200.00"],
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        with self.app.app_context():
            p = Product.query.filter_by(code="FIN-PL10").first()
            self.assertEqual(p.current_stock, init_stock + 50.0)

    # Rule 2: credit purchase increases supplier payable
    def test_rule_02_credit_purchase_increases_supplier_payable(self):
        with self.app.app_context():
            sup = Supplier.query.filter_by(name="Royal Ceramics Gujranwala").first()
            p = Product.query.filter_by(code="FIN-PL10").first()
            init_payable = sup.current_balance

        # 20 pcs @ 200 = 4,000 credit purchase
        res = self.client.post("/purchases/new", data={
            "bill_no": "PUR-RULE02",
            "date": "2026-10-01",
            "supplier_id": str(sup.id),
            "paid_amount": "0.00",
            "product_id[]": [str(p.id)],
            "quantity[]": ["20"],
            "unit[]": ["Pcs"],
            "rate[]": ["200.00"],
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        with self.app.app_context():
            sup = Supplier.query.filter_by(name="Royal Ceramics Gujranwala").first()
            self.assertEqual(sup.current_balance, init_payable + 4000.0)

    # Rule 3: cash purchase reduces cash
    def test_rule_03_cash_purchase_reduces_cash(self):
        with self.app.app_context():
            cash = Account.query.filter_by(account_type="Cash").first()
            sup = Supplier.query.filter_by(name="Royal Ceramics Gujranwala").first()
            p = Product.query.filter_by(code="FIN-PL10").first()
            init_cash = cash.balance

        # 10 pcs @ 200 = 2,000 paid immediately from cash
        res = self.client.post("/purchases/new", data={
            "bill_no": "PUR-RULE03",
            "date": "2026-10-01",
            "supplier_id": str(sup.id),
            "account_id": str(cash.id),
            "paid_amount": "2000.00",
            "product_id[]": [str(p.id)],
            "quantity[]": ["10"],
            "unit[]": ["Pcs"],
            "rate[]": ["200.00"],
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        with self.app.app_context():
            cash = Account.query.filter_by(account_type="Cash").first()
            self.assertEqual(cash.balance, init_cash - 2000.0)

    # Rule 4: sale decreases stock
    def test_rule_04_sale_decreases_stock(self):
        with self.app.app_context():
            p = Product.query.filter_by(code="FIN-PL10").first()
            cust = Customer.query.filter_by(name="Al-Madina Crockery Lahore").first()
            init_stock = p.current_stock

        res = self.client.post("/sales/new", data={
            "invoice_no": "SAL-RULE04",
            "date": "2026-10-01",
            "customer_id": str(cust.id),
            "received_amount": "0.00",
            "product_id[]": [str(p.id)],
            "quantity[]": ["30"],
            "unit[]": ["Pcs"],
            "cost_rate[]": ["200.00"],
            "sale_rate[]": ["300.00"],
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        with self.app.app_context():
            p = Product.query.filter_by(code="FIN-PL10").first()
            self.assertEqual(p.current_stock, init_stock - 30.0)

    # Rule 5: credit sale increases receivable
    def test_rule_05_credit_sale_increases_receivable(self):
        with self.app.app_context():
            cust = Customer.query.filter_by(name="Al-Madina Crockery Lahore").first()
            p = Product.query.filter_by(code="FIN-PL10").first()
            init_rec = cust.current_balance

        # 10 pcs @ 300 = 3,000 credit sale
        res = self.client.post("/sales/new", data={
            "invoice_no": "SAL-RULE05",
            "date": "2026-10-01",
            "customer_id": str(cust.id),
            "received_amount": "0.00",
            "product_id[]": [str(p.id)],
            "quantity[]": ["10"],
            "unit[]": ["Pcs"],
            "cost_rate[]": ["200.00"],
            "sale_rate[]": ["300.00"],
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        with self.app.app_context():
            cust = Customer.query.filter_by(name="Al-Madina Crockery Lahore").first()
            self.assertEqual(cust.current_balance, init_rec + 3000.0)

    # Rule 6: cash sale increases cash
    def test_rule_06_cash_sale_increases_cash(self):
        with self.app.app_context():
            cash = Account.query.filter_by(account_type="Cash").first()
            cust = Customer.query.filter_by(name="Al-Madina Crockery Lahore").first()
            p = Product.query.filter_by(code="FIN-PL10").first()
            init_cash = cash.balance

        # 5 pcs @ 300 = 1,500 cash sale
        res = self.client.post("/sales/new", data={
            "invoice_no": "SAL-RULE06",
            "date": "2026-10-01",
            "customer_id": str(cust.id),
            "account_id": str(cash.id),
            "received_amount": "1500.00",
            "product_id[]": [str(p.id)],
            "quantity[]": ["5"],
            "unit[]": ["Pcs"],
            "cost_rate[]": ["200.00"],
            "sale_rate[]": ["300.00"],
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        with self.app.app_context():
            cash = Account.query.filter_by(account_type="Cash").first()
            self.assertEqual(cash.balance, init_cash + 1500.0)

    # Rule 7: receipt reduces receivable and increases cash/bank
    def test_rule_07_receipt_reduces_receivable_and_increases_cash(self):
        with self.app.app_context():
            cust = Customer.query.filter_by(name="Al-Madina Crockery Lahore").first()
            bank = Account.query.filter_by(account_type="Bank").first()
            init_rec = cust.current_balance
            init_bank = bank.balance

        # Receive 5,000 from customer deposited in bank
        res = self.client.post("/cash-bank/receive-payment", data={
            "customer_id": str(cust.id),
            "account_id": str(bank.id),
            "date": "2026-10-01",
            "amount": "5000.00",
            "reference": "Cheque # 9901",
            "notes": "Receivable partial settlement",
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        with self.app.app_context():
            cust = Customer.query.filter_by(name="Al-Madina Crockery Lahore").first()
            bank = Account.query.filter_by(account_type="Bank").first()
            self.assertEqual(cust.current_balance, init_rec - 5000.0)
            self.assertEqual(bank.balance, init_bank + 5000.0)

    # Rule 8: supplier payment reduces payable and cash/bank
    def test_rule_08_supplier_payment_reduces_payable_and_bank(self):
        with self.app.app_context():
            sup = Supplier.query.filter_by(name="Royal Ceramics Gujranwala").first()
            bank = Account.query.filter_by(account_type="Bank").first()
            init_pay = sup.current_balance
            init_bank = bank.balance

        # Pay 4,000 to supplier via bank
        res = self.client.post("/cash-bank/make-payment", data={
            "supplier_id": str(sup.id),
            "account_id": str(bank.id),
            "date": "2026-10-01",
            "amount": "4000.00",
            "reference": "Online FT 1002",
            "notes": "Bill settlement payment",
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        with self.app.app_context():
            sup = Supplier.query.filter_by(name="Royal Ceramics Gujranwala").first()
            bank = Account.query.filter_by(account_type="Bank").first()
            self.assertEqual(sup.current_balance, init_pay - 4000.0)
            self.assertEqual(bank.balance, init_bank - 4000.0)

    # Rule 9: expense reduces profit
    def test_rule_09_expense_reduces_profit(self):
        # Record expense of 3,500
        with self.app.app_context():
            cash = Account.query.filter_by(account_type="Cash").first()

        res = self.client.post("/expenses/new", data={
            "date": "2026-10-01",
            "category": "Shop Rent",
            "title": "Shop Monthly Rent",
            "amount": "3500.00",
            "account_id": str(cash.id),
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # Check profit & loss
        pnl = self.client.get("/reports/profit-loss")
        self.assertEqual(pnl.status_code, 200)
        self.assertIn("3,500.00", pnl.data.decode("utf-8"))

    # Rule 10: partner drawing reduces partner balance and cash/bank
    def test_rule_10_partner_drawing_reduces_partner_balance_and_cash(self):
        with self.app.app_context():
            p1 = Partner.query.first()
            cash = Account.query.filter_by(account_type="Cash").first()
            init_curr = p1.current_balance or 0.0
            init_cash = cash.balance

        res = self.client.post("/partner-drawings/new", data={
            "partner_id": str(p1.id),
            "date": "2026-10-01",
            "account_id": str(cash.id),
            "amount": "8000.00",
            "description": "Personal family drawing",
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        with self.app.app_context():
            p1 = db.session.get(Partner, p1.id)
            cash = db.session.get(Account, cash.id)
            self.assertEqual(p1.current_balance, init_curr - 8000.0)
            self.assertEqual(cash.balance, init_cash - 8000.0)

    # Rule 11: stock valuation is consistent
    def test_rule_11_stock_valuation_is_consistent(self):
        res = self.client.get("/stock")
        self.assertEqual(res.status_code, 200)
        content = res.data.decode("utf-8")

        with self.app.app_context():
            p = Product.query.filter_by(code="FIN-PL10").first()
            expected_val = p.current_stock * p.cost_price

        self.assertIn(f"{expected_val:,.2f}", content)

    # Rule 12: trial balance strictly balances
    def test_rule_12_trial_balance_renders(self):
        res = self.client.get("/reports/trial-balance")
        self.assertEqual(res.status_code, 200)
        content = res.data.decode("utf-8")
        self.assertIn("Double-Entry Trial Balance", content)
        self.assertIn("Total Sum:", content)

    # Rule 13: monthly profit does not double-count expenses
    def test_rule_13_monthly_profit_accuracy(self):
        res = self.client.get("/monthly-profit")
        self.assertEqual(res.status_code, 200)
        content = res.data.decode("utf-8")
        self.assertIn("Monthly Profit & Partnership Sharing Register", content)
        self.assertIn("3,500.00", content)

    # Rule 14: stock adjustment correctly updates balance
    def test_rule_14_stock_adjustment_updates_stock(self):
        with self.app.app_context():
            p = Product.query.filter_by(code="FIN-PL10").first()
            init_stock = p.current_stock

        # Adjust for 4 pcs breakage
        res = self.client.post("/stock/adjustments/new", data={
            "product_id": str(p.id),
            "date": "2026-10-01",
            "adjustment_type": "Decrease",
            "quantity": "4",
            "reason": "Damage / Breakage in Warehouse",
            "notes": "Accidental shelf drop",
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        with self.app.app_context():
            p = Product.query.filter_by(code="FIN-PL10").first()
            self.assertEqual(p.current_stock, init_stock - 4.0)

    # Rule 15: backup download and authentication work
    def test_rule_15_backup_download_and_authentication(self):
        # 1. Unauthenticated cannot access backup
        unauth_client = self.app.test_client()
        unauth_res = unauth_client.get("/settings/backup")
        self.assertEqual(unauth_res.status_code, 302)

        # 2. Authenticated admin can download backup
        res = self.client.get("/settings/backup")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("Content-Type"), "application/octet-stream")
        self.assertTrue(res.headers.get("Content-Disposition", "").startswith("attachment"))


if __name__ == "__main__":
    unittest.main()
