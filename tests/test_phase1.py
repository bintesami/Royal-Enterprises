import os
import sys
import unittest
from sqlalchemy import inspect

# Ensure crockery_app is first in Python path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
app_dir = os.path.join(base_dir, "crockery_app")
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from app import create_app, db
from models.user import User, Role
from models.partner import Partner
from models.cash_bank import Account


class Phase1TestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use a temporary in-memory or dedicated test database
        cls.test_db_path = os.path.join(base_dir, "test_database.db")
        cls.app = create_app({
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{cls.test_db_path}",
        })
        cls.client = cls.app.test_client()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_db_path):
            try:
                os.remove(cls.test_db_path)
            except Exception:
                pass

    def test_01_all_17_database_tables_created(self):
        """Verify all 17 accounting and foundational tables exist in SQLite."""
        with self.app.app_context():
            inspector = inspect(db.engine)
            tables = set(inspector.get_table_names())

            required_tables = {
                "users",
                "roles",
                "partners",
                "customers",
                "suppliers",
                "products",
                "purchases",
                "purchase_items",
                "sales",
                "sale_items",
                "expenses",
                "cash_bank_transactions",
                "stock_movements",
                "partner_drawings",
                "accounts",
                "journal_entries",
                "journal_lines",
            }

            missing = required_tables - tables
            self.assertEqual(len(missing), 0, f"Missing tables in database: {missing}")

    def test_02_default_admin_user_and_password_hashing(self):
        """Verify default admin user exists and password is secure hash."""
        with self.app.app_context():
            admin = User.query.filter_by(username="admin").first()
            self.assertIsNotNone(admin, "Default admin user was not found.")
            self.assertNotEqual(admin.password_hash, "admin123", "Password must be hashed, not plain text.")
            self.assertTrue(admin.check_password("admin123"), "Admin password verification failed.")
            self.assertFalse(admin.check_password("wrongpass"), "Admin password should reject wrong password.")
            self.assertEqual(admin.role, "Admin")
            self.assertTrue(admin.is_active)

    def test_03_default_roles_seeded(self):
        """Verify standard roles are seeded."""
        with self.app.app_context():
            roles = [r.name for r in Role.query.all()]
            expected_roles = ["Admin", "Accountant", "Sales", "Purchase", "Viewer"]
            for role in expected_roles:
                self.assertIn(role, roles, f"Role '{role}' missing from database.")

    def test_04_default_partners_seeded(self):
        """Verify default 50/50 partners from Excel specification."""
        with self.app.app_context():
            partners = Partner.query.all()
            self.assertGreaterEqual(len(partners), 2, "Expected at least 2 partners.")
            for p in partners:
                self.assertEqual(p.profit_share_percentage, 50.0)

    def test_05_default_accounts_seeded(self):
        """Verify default cash and bank accounts exist."""
        with self.app.app_context():
            cash = Account.query.filter_by(account_type="Cash").first()
            bank = Account.query.filter_by(account_type="Bank").first()
            self.assertIsNotNone(cash, "Cash in Hand account not found.")
            self.assertIsNotNone(bank, "Bank account not found.")

    def test_06_unauthenticated_dashboard_redirects_to_login(self):
        """Verify dashboard route requires authentication."""
        response = self.client.get("/", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_07_login_page_renders_successfully(self):
        """Verify login page renders."""
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        content = response.data.decode("utf-8")
        self.assertIn("Crockery Accounts", content)
        self.assertIn("Wholesale Partnership Accounting System", content)

    def test_08_login_with_invalid_credentials_fails(self):
        """Verify invalid login attempt fails with error flash."""
        response = self.client.post("/login", data={
            "username": "admin",
            "password": "wrongpassword"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        content = response.data.decode("utf-8")
        self.assertIn("Invalid username or password", content)

    def test_09_login_with_valid_admin_credentials_succeeds(self):
        """Verify successful login redirects to dashboard."""
        response = self.client.post("/login", data={
            "username": "admin",
            "password": "admin123"
        }, follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/", response.headers["Location"])

    def test_10_authenticated_dashboard_has_all_11_excel_modules(self):
        """Verify dashboard renders all 11 Excel modules in the sidebar."""
        # Login
        self.client.post("/login", data={"username": "admin", "password": "admin123"})
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        content = response.data.decode("utf-8")

        # 11 original Excel workbook sheets
        excel_modules = [
            "Dashboard",
            "Partners Capital",
            "Purchases",
            "Sales",
            "Customer Ledger",
            "Supplier Ledger",
            "Expenses",
            "Stock",
            "Cash & Bank",
            "Partner Drawings",
            "Monthly Profit",
        ]

        for mod in excel_modules:
            self.assertIn(mod, content, f"Module '{mod}' was not found in sidebar!")

    def test_11_dashboard_kpis_and_quick_actions(self):
        """Verify 8 financial KPI cards and quick actions on dashboard."""
        self.client.post("/login", data={"username": "admin", "password": "admin123"})
        response = self.client.get("/")
        content = response.data.decode("utf-8")

        # 8 KPI cards
        kpis = [
            "Total Sales",
            "Total Purchases",
            "Receivable",
            "Payable",
            "Stock Value",
            "Cash Balance",
            "Bank Balance",
            "Net Profit",
        ]
        for kpi in kpis:
            self.assertIn(kpi, content, f"KPI '{kpi}' missing from dashboard.")

        # Quick actions
        quick_actions = [
            "New Purchase",
            "New Sale",
            "Receive Payment",
            "Make Payment",
            "Add Expense",
        ]
        for action in quick_actions:
            self.assertIn(action, content, f"Quick action '{action}' missing from dashboard.")

    def test_12_logout_flow(self):
        """Verify logout clears session and redirects to login."""
        self.client.post("/login", data={"username": "admin", "password": "admin123"})
        logout_response = self.client.get("/logout", follow_redirects=False)
        self.assertEqual(logout_response.status_code, 302)
        self.assertIn("/login", logout_response.headers["Location"])

        # Subsequent dashboard visit should redirect back to login
        dash_response = self.client.get("/", follow_redirects=False)
        self.assertEqual(dash_response.status_code, 302)
        self.assertIn("/login", dash_response.headers["Location"])


if __name__ == "__main__":
    unittest.main()
