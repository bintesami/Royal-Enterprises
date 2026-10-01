import os
import sys

# Ensure current directory is in sys.path for direct imports
basedir = os.path.abspath(os.path.dirname(__file__))
if basedir not in sys.path:
    sys.path.insert(0, basedir)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Alias module so both 'app' and 'crockery_app.app' resolve to same instance
sys.modules.setdefault("app", sys.modules[__name__])

db = SQLAlchemy()
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    from models.user import User
    try:
        return db.session.get(User, int(user_id))
    except Exception:
        return None


def seed_initial_data():
    """Seed foundational data required for Phase 1 on first launch."""
    from models.user import User, Role
    from models.partner import Partner
    from models.cash_bank import Account

    # 1. Seed standard roles
    roles = ["Admin", "Accountant", "Sales", "Purchase", "Viewer"]
    for role_name in roles:
        if not Role.query.filter_by(name=role_name).first():
            db.session.add(Role(name=role_name, description=f"{role_name} Role"))

    # 2. Seed default admin user if not present
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(
            username="admin",
            full_name="System Administrator",
            role="Admin",
            is_active=True,
        )
        admin.set_password("admin123")
        db.session.add(admin)

    # 3. Seed default 50/50 partners from Excel Dashboard specification
    if Partner.query.count() == 0:
        p1 = Partner(
            name="Partner 1",
            profit_share_percentage=50.0,
            capital_balance=0.0,
            current_balance=0.0,
        )
        p2 = Partner(
            name="Partner 2",
            profit_share_percentage=50.0,
            capital_balance=0.0,
            current_balance=0.0,
        )
        db.session.add_all([p1, p2])

    # 4. Seed default accounts (Cash in Hand & Bank)
    if Account.query.count() == 0:
        cash_account = Account(
            account_name="Cash in Hand",
            account_type="Cash",
            balance=0.0,
        )
        bank_account = Account(
            account_name="Main Bank Account",
            account_type="Bank",
            balance=0.0,
        )
        db.session.add_all([cash_account, bank_account])

    db.session.commit()


def create_app(test_config=None):
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "change-this-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///" + os.path.join(basedir, "database.db")
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.masters import masters_bp
    from routes.purchases import purchases_bp
    from routes.sales import sales_bp
    from routes.stock import stock_bp
    from routes.ledgers import ledgers_bp
    from routes.cash_bank import cash_bank_bp
    from routes.import_excel import import_bp
    from routes.expenses import expenses_bp
    from routes.partners import partners_bp
    from routes.reports import reports_bp
    from routes.settings import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(masters_bp)
    app.register_blueprint(purchases_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(stock_bp)
    app.register_blueprint(ledgers_bp)
    app.register_blueprint(cash_bank_bp)
    app.register_blueprint(import_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(partners_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)

    @app.context_processor
    def inject_globals():
        return {
            "CURRENCY": "PKR",
            "BUSINESS_NAME": "Crockery Wholesale Partnership Accounting System",
        }

    with app.app_context():
        import models  # Register all models with metadata
        db.create_all()
        # Ensure new columns exist on SQLite without losing data
        try:
            with db.engine.connect() as conn:
                exp_cols = [c[1] for c in conn.execute(db.text("PRAGMA table_info(expenses)")).fetchall()]
                if "expense_no" not in exp_cols:
                    conn.execute(db.text("ALTER TABLE expenses ADD COLUMN expense_no VARCHAR(50)"))
                if "payee" not in exp_cols:
                    conn.execute(db.text("ALTER TABLE expenses ADD COLUMN payee VARCHAR(150)"))
                if "reference" not in exp_cols:
                    conn.execute(db.text("ALTER TABLE expenses ADD COLUMN reference VARCHAR(100)"))

                draw_cols = [c[1] for c in conn.execute(db.text("PRAGMA table_info(partner_drawings)")).fetchall()]
                if "approved_by" not in draw_cols:
                    conn.execute(db.text("ALTER TABLE partner_drawings ADD COLUMN approved_by VARCHAR(100)"))
                if "remarks" not in draw_cols:
                    conn.execute(db.text("ALTER TABLE partner_drawings ADD COLUMN remarks VARCHAR(255)"))
                conn.commit()
        except Exception:
            pass

        seed_initial_data()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000,
    )
