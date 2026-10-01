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
from models.customer import Customer
from models.supplier import Supplier
from models.cash_bank import Account, CashBankTransaction


class Phase56TestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db_path = os.path.join(base_dir, "test_phase56.db")
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

    def test_01_account_management(self):
        """Test creating a new bank account."""
        response = self.client.post("/cash-bank/accounts", data={
            "account_name": "Meezan Bank - Main Business",
            "account_type": "Bank",
            "bank_name": "Meezan Bank Ltd",
            "account_number": "0101-123456789",
            "opening_balance": "100000.00",
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            acc = Account.query.filter_by(account_name="Meezan Bank - Main Business").first()
            self.assertIsNotNone(acc)
            self.assertEqual(acc.account_type, "Bank")
            self.assertEqual(acc.balance, 100000.0)

    def test_02_receive_customer_payment_voucher(self):
        """
        Verify:
        Receive Payment from Customer -> Cash Account Increases -> Customer Receivable Balance Decreases.
        """
        with self.app.app_context():
            cust = Customer(name="Al-Madina Store", opening_balance=10000.0, current_balance=10000.0)
            cash = Account.query.filter_by(account_type="Cash").first()
            cash.balance = 5000.0
            db.session.add(cust)
            db.session.commit()

            cust_id = cust.id
            cash_id = cash.id

        # Receive 4,000 PKR from Al-Madina Store into Cash
        response = self.client.post("/cash-bank/receive-payment", data={
            "customer_id": cust_id,
            "account_id": cash_id,
            "amount": "4000.00",
            "date": "2026-10-01",
            "reference": "RV-001",
            "notes": "Partial settlement of past delivery",
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            # Cash should increase by 4,000 -> 9,000
            updated_cash = db.session.get(Account, cash_id)
            self.assertEqual(updated_cash.balance, 9000.0)

            # Customer balance should decrease by 4,000 -> 6,000
            updated_cust = db.session.get(Customer, cust_id)
            self.assertEqual(updated_cust.current_balance, 6000.0)

            # Cash transaction logged
            txn = CashBankTransaction.query.filter_by(transaction_type="Customer Receipt", amount=4000.0).first()
            self.assertIsNotNone(txn)
            self.assertEqual(txn.reference_id, cust_id)

    def test_03_make_supplier_payment_voucher(self):
        """
        Verify:
        Make Payment to Supplier -> Cash Account Decreases -> Supplier Payable Balance Decreases.
        """
        with self.app.app_context():
            sup = Supplier(name="Gujranwala Crockery Mill", opening_balance=8000.0, current_balance=8000.0)
            cash = Account.query.filter_by(account_type="Cash").first()
            # Current cash is 9,000 from previous test
            db.session.add(sup)
            db.session.commit()

            sup_id = sup.id
            cash_id = cash.id

        # Pay 5,000 PKR to Supplier from Cash
        response = self.client.post("/cash-bank/make-payment", data={
            "supplier_id": sup_id,
            "account_id": cash_id,
            "amount": "5000.00",
            "date": "2026-10-01",
            "reference": "PV-001",
            "notes": "Payment towards monthly procurement",
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            # Cash should decrease from 9,000 to 4,000
            updated_cash = db.session.get(Account, cash_id)
            self.assertEqual(updated_cash.balance, 4000.0)

            # Supplier payable should decrease from 8,000 to 3,000
            updated_sup = db.session.get(Supplier, sup_id)
            self.assertEqual(updated_sup.current_balance, 3000.0)

            # Cash transaction logged
            txn = CashBankTransaction.query.filter_by(transaction_type="Supplier Payment", amount=5000.0).first()
            self.assertIsNotNone(txn)
            self.assertEqual(txn.reference_id, sup_id)

    def test_04_inter_account_fund_transfer(self):
        """
        Verify:
        Fund Transfer: Cash in Hand (4,000) -> Meezan Bank (100,000)
        Transfer 2,000 -> Cash becomes 2,000, Bank becomes 102,000.
        Total liquidity (104,000) is preserved.
        """
        with self.app.app_context():
            cash = Account.query.filter_by(account_type="Cash").first()
            bank = Account.query.filter_by(account_name="Meezan Bank - Main Business").first()
            cash_id = cash.id
            bank_id = bank.id

        response = self.client.post("/cash-bank/transfer", data={
            "from_account_id": cash_id,
            "to_account_id": bank_id,
            "amount": "2000.00",
            "date": "2026-10-01",
            "reference": "DEP-001",
            "notes": "Bank deposit",
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            updated_cash = db.session.get(Account, cash_id)
            updated_bank = db.session.get(Account, bank_id)

            self.assertEqual(updated_cash.balance, 2000.0)
            self.assertEqual(updated_bank.balance, 102000.0)
            self.assertEqual(updated_cash.balance + updated_bank.balance, 104000.0)

    def test_05_cash_bank_book_view(self):
        """Verify Cash & Bank Book renders with columns matching Excel."""
        response = self.client.get("/cash-bank")
        self.assertEqual(response.status_code, 200)
        content = response.data.decode("utf-8")

        self.assertIn("Cash & Bank Book", content)
        self.assertIn("Customer Receipt", content)
        self.assertIn("Supplier Payment", content)
        self.assertIn("Cash in Hand", content)
        self.assertIn("4,000.00", content)
        self.assertIn("5,000.00", content)

    def test_06_customer_running_ledger(self):
        """Verify Customer Ledger displays running balances."""
        response = self.client.get("/customer-ledger")
        self.assertEqual(response.status_code, 200)
        content = response.data.decode("utf-8")

        self.assertIn("Customer Receivable Ledger", content)
        self.assertIn("Al-Madina Store", content)
        self.assertIn("4,000.00", content)  # credit payment received
        self.assertIn("6,000.00", content)  # running balance

    def test_07_supplier_running_ledger(self):
        """Verify Supplier Ledger displays running balances."""
        response = self.client.get("/supplier-ledger")
        self.assertEqual(response.status_code, 200)
        content = response.data.decode("utf-8")

        self.assertIn("Supplier Payable Ledger", content)
        self.assertIn("Gujranwala Crockery Mill", content)
        self.assertIn("5,000.00", content)  # debit payment settled
        self.assertIn("3,000.00", content)  # running balance


if __name__ == "__main__":
    unittest.main()
