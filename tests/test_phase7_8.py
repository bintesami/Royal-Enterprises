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
from models.partner import Partner, PartnerCapitalTransaction
from models.expense import Expense
from models.cash_bank import Account, CashBankTransaction, PartnerDrawing
from models.product import Product
from models.customer import Customer
from models.sale import Sale, SaleItem


class Phase78TestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db_path = os.path.join(base_dir, "test_phase78.db")
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

        # Initialize base balances
        with cls.app.app_context():
            cash = Account.query.filter_by(account_type="Cash").first()
            if cash:
                cash.balance = 50000.0
            bank = Account.query.filter_by(account_type="Bank").first()
            if bank:
                bank.balance = 200000.0
            db.session.commit()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_db_path):
            try:
                os.remove(cls.test_db_path)
            except Exception:
                pass

    def test_01_record_expense_cash(self):
        """Test recording an expense paid via Cash in Hand."""
        with self.app.app_context():
            cash_acc = Account.query.filter_by(account_type="Cash").first()
            initial_balance = cash_acc.balance

        response = self.client.post("/expenses/new", data={
            "date": "2026-10-01",
            "category": "Tea & Refreshment",
            "title": "Shop Daily Tea & Refreshment",
            "payee": "Hotel Al-Karam",
            "amount": "1500.00",
            "account_id": str(cash_acc.id),
            "reference": "Slip # 401",
            "description": "Tea and snacks for staff & visiting customers",
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            exp = Expense.query.filter_by(title="Shop Daily Tea & Refreshment").first()
            self.assertIsNotNone(exp)
            self.assertEqual(exp.amount, 1500.0)
            self.assertEqual(exp.category, "Tea & Refreshment")
            self.assertTrue(exp.expense_no.startswith("EXP-"))

            # Check cash deduction
            cash_acc = db.session.get(Account, cash_acc.id)
            self.assertEqual(cash_acc.balance, initial_balance - 1500.0)

            # Check CashBankTransaction logged
            cb_tx = CashBankTransaction.query.filter_by(
                reference_type="Expense", reference_id=exp.id
            ).first()
            self.assertIsNotNone(cb_tx)
            self.assertEqual(cb_tx.transaction_type, "Expense")
            self.assertEqual(cb_tx.amount, 1500.0)

    def test_02_record_expense_bank(self):
        """Test recording an expense paid via Bank Account."""
        with self.app.app_context():
            bank_acc = Account.query.filter_by(account_type="Bank").first()
            initial_balance = bank_acc.balance

        response = self.client.post("/expenses/new", data={
            "date": "2026-10-01",
            "category": "Electricity Bill",
            "title": "IESCO Electricity Bill Oct",
            "payee": "IESCO",
            "amount": "12500.00",
            "account_id": str(bank_acc.id),
            "reference": "Consumer # 128391823",
            "description": "Monthly shop electricity bill online payment",
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            exp = Expense.query.filter_by(title="IESCO Electricity Bill Oct").first()
            self.assertIsNotNone(exp)
            self.assertEqual(exp.amount, 12500.0)

            # Check bank deduction
            bank_acc = db.session.get(Account, bank_acc.id)
            self.assertEqual(bank_acc.balance, initial_balance - 12500.0)

        # Check in Cash & Bank Book
        book_res = self.client.get("/cash-bank")
        self.assertEqual(book_res.status_code, 200)
        content = book_res.data.decode("utf-8")
        self.assertIn("IESCO Electricity Bill Oct", content)
        self.assertIn("12,500.00", content)

    def test_03_partner_capital_added_with_bank_deposit(self):
        """Test recording partner capital injection deposited into bank."""
        with self.app.app_context():
            p1 = Partner.query.first()
            initial_cap = p1.capital_balance or 0.0
            initial_curr = p1.current_balance or 0.0
            bank_acc = Account.query.filter_by(account_type="Bank").first()
            initial_bank = bank_acc.balance

        response = self.client.post("/partners/capital/new", data={
            "partner_id": str(p1.id),
            "date": "2026-10-01",
            "transaction_type": "Capital Added",
            "amount": "250000.00",
            "account_id": str(bank_acc.id),
            "description": "Additional working capital for new stock batch",
            "reference": "Chq # 5501",
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            p1 = db.session.get(Partner, p1.id)
            self.assertEqual(p1.capital_balance, initial_cap + 250000.0)
            self.assertEqual(p1.current_balance, initial_curr + 250000.0)

            bank_acc = db.session.get(Account, bank_acc.id)
            self.assertEqual(bank_acc.balance, initial_bank + 250000.0)

            # Check PartnerCapitalTransaction
            tx = PartnerCapitalTransaction.query.filter_by(
                partner_id=p1.id, transaction_type="Capital Added", amount=250000.0
            ).first()
            self.assertIsNotNone(tx)

    def test_04_partner_drawing_with_cash_withdrawal(self):
        """Test recording partner drawing withdrawn from cash in hand."""
        with self.app.app_context():
            p1 = Partner.query.first()
            initial_curr = p1.current_balance
            cash_acc = Account.query.filter_by(account_type="Cash").first()
            initial_cash = cash_acc.balance

        response = self.client.post("/partner-drawings/new", data={
            "partner_id": str(p1.id),
            "date": "2026-10-01",
            "account_id": str(cash_acc.id),
            "amount": "20000.00",
            "description": "Personal family expense withdrawal",
            "approved_by": "Mutual Partner Consent",
            "remarks": "Cash withdrawal voucher",
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            p1 = db.session.get(Partner, p1.id)
            self.assertEqual(p1.current_balance, initial_curr - 20000.0)

            cash_acc = db.session.get(Account, cash_acc.id)
            self.assertEqual(cash_acc.balance, initial_cash - 20000.0)

            # Check PartnerDrawing entry
            drawing = PartnerDrawing.query.filter_by(partner_id=p1.id, amount=20000.0).first()
            self.assertIsNotNone(drawing)
            self.assertEqual(drawing.approved_by, "Mutual Partner Consent")

            # Check Cash & Bank Book transaction
            cb_tx = CashBankTransaction.query.filter_by(
                reference_type="PartnerDrawing", reference_id=drawing.id
            ).first()
            self.assertIsNotNone(cb_tx)
            self.assertEqual(cb_tx.transaction_type, "Partner Drawing")

    def test_05_partner_running_statement(self):
        """Test generating partner statement with chronological running balance."""
        with self.app.app_context():
            p1 = Partner.query.first()

        response = self.client.get(f"/partners/{p1.id}/statement")
        self.assertEqual(response.status_code, 200)
        content = response.data.decode("utf-8")

        self.assertIn("Partner Individual Account Statement", content)
        self.assertIn(p1.name, content)
        self.assertIn("Capital Added", content)
        self.assertIn("250,000.00", content)
        self.assertIn("Partner Drawing", content)
        self.assertIn("20,000.00", content)

    def test_06_monthly_profit_report(self):
        """Test monthly profit calculation and 50/50 partnership share."""
        # Create a test sale with known gross profit
        with self.app.app_context():
            cust = Customer.query.first()
            if not cust:
                cust = Customer(name="Wholesale Test Store")
                db.session.add(cust)
                db.session.flush()

            prod = Product.query.first()
            if not prod:
                prod = Product(code="TEST-01", name="Test Item", cost_price=100.0, current_stock=500.0)
                db.session.add(prod)
                db.session.flush()

            sale = Sale(
                invoice_no="INV-TEST-PROFIT",
                date=datetime(2026, 10, 1),
                customer_id=cust.id,
                total_sale=50000.0,
                total_cost=35000.0,
                gross_profit=15000.0,
                received_amount=50000.0,
                balance_amount=0.0,
            )
            db.session.add(sale)
            item = SaleItem(
                sale=sale,
                product_id=prod.id,
                quantity=100,
                cost_rate=prod.cost_price or 100.0,
                sale_rate=500.0,
                cost_total=10000.0,
                sale_total=50000.0,
                profit=40000.0,
            )
            db.session.add(item)
            db.session.commit()

        response = self.client.get("/monthly-profit")
        self.assertEqual(response.status_code, 200)
        content = response.data.decode("utf-8")

        self.assertIn("Monthly Profit & Partnership Sharing Register", content)
        self.assertIn("Cost of Goods Sold (COGS)", content)

    def test_07_dashboard_expenses_and_capital(self):
        """Test that dashboard properly reflects expenses and capital pool."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        content = response.data.decode("utf-8")
        self.assertIn("Total Capital Pool", content)
        self.assertIn("Add Expense", content)
        self.assertIn("Partner Drawings", content)
        self.assertIn("Monthly Profit", content)


if __name__ == "__main__":
    unittest.main()
