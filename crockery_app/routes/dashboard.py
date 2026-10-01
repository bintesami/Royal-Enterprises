from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func

from app import db
from models.sale import Sale
from models.purchase import Purchase
from models.customer import Customer
from models.supplier import Supplier
from models.product import Product
from models.expense import Expense
from models.partner import Partner
from models.cash_bank import Account

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    # Dynamic calculations with fallback to 0.0 for Phase 1
    total_sales = db.session.query(func.coalesce(func.sum(Sale.total_sale), 0.0)).scalar() or 0.0
    total_purchases = db.session.query(func.coalesce(func.sum(Purchase.total_amount), 0.0)).scalar() or 0.0
    receivable = db.session.query(func.coalesce(func.sum(Customer.current_balance), 0.0)).scalar() or 0.0
    payable = db.session.query(func.coalesce(func.sum(Supplier.current_balance), 0.0)).scalar() or 0.0
    
    # Stock value: sum(current_stock * cost_price)
    stock_value = db.session.query(
        func.coalesce(func.sum(Product.current_stock * Product.cost_price), 0.0)
    ).scalar() or 0.0

    # Cash and Bank balances
    cash_balance = db.session.query(
        func.coalesce(func.sum(Account.balance), 0.0)
    ).filter(Account.account_type == "Cash").scalar() or 0.0

    bank_balance = db.session.query(
        func.coalesce(func.sum(Account.balance), 0.0)
    ).filter(Account.account_type == "Bank").scalar() or 0.0

    total_expenses = db.session.query(func.coalesce(func.sum(Expense.amount), 0.0)).scalar() or 0.0
    total_gross_profit = db.session.query(func.coalesce(func.sum(Sale.gross_profit), 0.0)).scalar() or 0.0
    net_profit = total_gross_profit - total_expenses

    # Partners
    partners = Partner.query.order_by(Partner.id.asc()).all()

    # Stock counts
    total_products_count = Product.query.count()
    low_stock_count = Product.query.filter(Product.current_stock <= Product.min_stock_alert).count()

    total_capital = sum(p.capital_balance or 0.0 for p in partners)

    metrics = {
        "total_sales": total_sales,
        "total_purchases": total_purchases,
        "receivable": receivable,
        "payable": payable,
        "stock_value": stock_value,
        "cash_balance": cash_balance,
        "bank_balance": bank_balance,
        "total_expenses": total_expenses,
        "total_gross_profit": total_gross_profit,
        "net_profit": net_profit,
        "total_capital": total_capital,
        "total_products_count": total_products_count,
        "low_stock_count": low_stock_count,
    }

    return render_template(
        "dashboard.html",
        metrics=metrics,
        partners=partners,
    )
