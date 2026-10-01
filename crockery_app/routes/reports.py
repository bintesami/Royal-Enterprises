from datetime import datetime
from collections import defaultdict
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy import func
from app import db
from models.sale import Sale, SaleItem
from models.purchase import Purchase
from models.expense import Expense
from models.partner import Partner, PartnerCapitalTransaction
from models.customer import Customer
from models.supplier import Supplier
from models.product import Product
from models.cash_bank import Account, PartnerDrawing

reports_bp = Blueprint("reports", __name__)


# ================= 1. MONTHLY PROFIT & 50/50 SHARING =================
@reports_bp.route("/monthly-profit")
@login_required
def monthly_profit():
    partners = Partner.query.order_by(Partner.id.asc()).all()
    p1 = partners[0] if len(partners) > 0 else None
    p2 = partners[1] if len(partners) > 1 else None

    monthly_data = defaultdict(
        lambda: {
            "month_key": "",
            "month_label": "",
            "sales": 0.0,
            "cogs": 0.0,
            "gross_profit": 0.0,
            "expenses": 0.0,
            "net_profit": 0.0,
            "p1_share": 0.0,
            "p2_share": 0.0,
        }
    )

    sales = Sale.query.order_by(Sale.date.asc()).all()
    for s in sales:
        m_key = s.date.strftime("%Y-%m")
        entry = monthly_data[m_key]
        entry["month_key"] = m_key
        entry["month_label"] = s.date.strftime("%B %Y")
        entry["sales"] += s.total_sale or 0.0
        sale_cogs = (
            s.total_cost
            if (s.total_cost is not None and s.total_cost > 0)
            else sum(
                (item.quantity or 0.0) * (item.cost_rate or 0.0)
                for item in s.items
            )
        )
        entry["cogs"] += sale_cogs
        entry["gross_profit"] += (
            s.gross_profit
            if s.gross_profit is not None
            else ((s.total_sale or 0.0) - sale_cogs)
        )

    expenses = Expense.query.order_by(Expense.date.asc()).all()
    for exp in expenses:
        m_key = exp.date.strftime("%Y-%m")
        entry = monthly_data[m_key]
        if not entry["month_key"]:
            entry["month_key"] = m_key
            entry["month_label"] = exp.date.strftime("%B %Y")
        entry["expenses"] += exp.amount or 0.0

    if not monthly_data:
        now = datetime.utcnow()
        cur_key = now.strftime("%Y-%m")
        monthly_data[cur_key] = {
            "month_key": cur_key,
            "month_label": now.strftime("%B %Y"),
            "sales": 0.0,
            "cogs": 0.0,
            "gross_profit": 0.0,
            "expenses": 0.0,
            "net_profit": 0.0,
            "p1_share": 0.0,
            "p2_share": 0.0,
        }

    rows = []
    p1_ratio = (p1.profit_share_percentage / 100.0) if p1 else 0.5
    p2_ratio = (p2.profit_share_percentage / 100.0) if p2 else 0.5

    for m_key in sorted(monthly_data.keys(), reverse=True):
        row = monthly_data[m_key]
        row["net_profit"] = row["gross_profit"] - row["expenses"]
        row["p1_share"] = row["net_profit"] * p1_ratio
        row["p2_share"] = row["net_profit"] * p2_ratio
        rows.append(row)

    total_sales = sum(r["sales"] for r in rows)
    total_cogs = sum(r["cogs"] for r in rows)
    total_gross = sum(r["gross_profit"] for r in rows)
    total_exp = sum(r["expenses"] for r in rows)
    total_net = sum(r["net_profit"] for r in rows)
    total_p1 = sum(r["p1_share"] for r in rows)
    total_p2 = sum(r["p2_share"] for r in rows)

    return render_template(
        "reports/monthly_profit.html",
        rows=rows,
        partners=partners,
        p1=p1,
        p2=p2,
        total_sales=total_sales,
        total_cogs=total_cogs,
        total_gross=total_gross,
        total_exp=total_exp,
        total_net=total_net,
        total_p1=total_p1,
        total_p2=total_p2,
    )


@reports_bp.route("/monthly-profit/distribute", methods=["POST"])
@login_required
def distribute_profit():
    month_key = request.form.get("month_key")
    if not month_key:
        flash("Invalid month specified for profit distribution.", "danger")
        return redirect(url_for("reports.monthly_profit"))

    ref = f"PROFIT-{month_key}"
    existing = PartnerCapitalTransaction.query.filter_by(reference=ref).first()
    if existing:
        flash(f"Profit for month {month_key} has already been posted to partners.", "warning")
        return redirect(url_for("reports.monthly_profit"))

    try:
        parts = month_key.split("-")
        year, month = int(parts[0]), int(parts[1])
        start_dt = datetime(year, month, 1)
        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1
        end_dt = datetime(next_year, next_month, 1)
    except Exception:
        flash("Date parsing error.", "danger")
        return redirect(url_for("reports.monthly_profit"))

    sales = Sale.query.filter(Sale.date >= start_dt, Sale.date < end_dt).all()
    month_sales = sum(s.total_sale or 0.0 for s in sales)
    month_cogs = sum(
        (
            s.total_cost
            if (s.total_cost is not None and s.total_cost > 0)
            else sum(
                (item.quantity or 0.0) * (item.cost_rate or 0.0)
                for item in s.items
            )
        )
        for s in sales
    )
    month_expenses = (
        db.session.query(func.coalesce(func.sum(Expense.amount), 0.0))
        .filter(Expense.date >= start_dt, Expense.date < end_dt)
        .scalar()
        or 0.0
    )

    net_profit = (month_sales - month_cogs) - month_expenses

    if net_profit <= 0:
        flash(f"Net profit for {month_key} is PKR {net_profit:,.2f}. Distribution is only applicable on positive net profits.", "warning")
        return redirect(url_for("reports.monthly_profit"))

    partners = Partner.query.order_by(Partner.id.asc()).all()
    for p in partners:
        share_amount = net_profit * (p.profit_share_percentage / 100.0)
        p.current_balance = (p.current_balance or 0.0) + share_amount

        cap_tx = PartnerCapitalTransaction(
            partner_id=p.id,
            date=datetime.utcnow(),
            transaction_type="Profit Share",
            amount=share_amount,
            description=f"Monthly profit share for {start_dt.strftime('%B %Y')} ({p.profit_share_percentage:g}%)",
            reference=ref,
        )
        db.session.add(cap_tx)

    db.session.commit()
    flash(f"Successfully distributed net profit of PKR {net_profit:,.2f} for {start_dt.strftime('%B %Y')} among partners.", "success")
    return redirect(url_for("reports.monthly_profit"))


# ================= 2. TRIAL BALANCE =================
@reports_bp.route("/reports/trial-balance")
@login_required
def trial_balance():
    # 1. Cash Accounts
    cash_accounts = Account.query.filter_by(account_type="Cash").all()
    # 2. Bank Accounts
    bank_accounts = Account.query.filter_by(account_type="Bank").all()
    # 3. Customer Receivables
    receivables_total = (
        db.session.query(func.coalesce(func.sum(Customer.current_balance), 0.0)).scalar()
        or 0.0
    )
    # 4. Inventory Valuation
    inventory_val = (
        db.session.query(
            func.coalesce(func.sum(Product.current_stock * Product.cost_price), 0.0)
        ).scalar()
        or 0.0
    )
    # 5. Cost of Goods Sold
    cogs_total = (
        db.session.query(func.coalesce(func.sum(Sale.total_cost), 0.0)).scalar()
        or 0.0
    )
    # 6. Operating Expenses
    expenses_total = (
        db.session.query(func.coalesce(func.sum(Expense.amount), 0.0)).scalar()
        or 0.0
    )
    # 7. Partner Drawings
    drawings_total = (
        db.session.query(func.coalesce(func.sum(PartnerDrawing.amount), 0.0)).scalar()
        or 0.0
    )

    # 8. Supplier Payables
    payables_total = (
        db.session.query(func.coalesce(func.sum(Supplier.current_balance), 0.0)).scalar()
        or 0.0
    )
    # 9. Sales Revenue
    revenue_total = (
        db.session.query(func.coalesce(func.sum(Sale.total_sale), 0.0)).scalar()
        or 0.0
    )
    # 10. Partner Capital
    capital_total = (
        db.session.query(func.coalesce(func.sum(Partner.capital_balance), 0.0)).scalar()
        or 0.0
    )

    items = []

    # Cash in Hand
    for acc in cash_accounts:
        bal = acc.balance or 0.0
        items.append({
            "account": f"Cash Account — {acc.account_name}",
            "type": "Asset",
            "debit": bal if bal >= 0 else 0.0,
            "credit": abs(bal) if bal < 0 else 0.0,
        })

    # Bank Accounts
    for acc in bank_accounts:
        bal = acc.balance or 0.0
        items.append({
            "account": f"Bank Account — {acc.account_name} ({acc.bank_name or 'Bank'})",
            "type": "Asset",
            "debit": bal if bal >= 0 else 0.0,
            "credit": abs(bal) if bal < 0 else 0.0,
        })

    # Accounts Receivable
    items.append({
        "account": "Accounts Receivable (Customer Ledger)",
        "type": "Asset",
        "debit": receivables_total if receivables_total >= 0 else 0.0,
        "credit": abs(receivables_total) if receivables_total < 0 else 0.0,
    })

    # Merchandise Inventory
    items.append({
        "account": "Merchandise Inventory (Stock Asset at Cost)",
        "type": "Asset",
        "debit": inventory_val if inventory_val >= 0 else 0.0,
        "credit": 0.0,
    })

    # COGS
    items.append({
        "account": "Cost of Goods Sold (COGS)",
        "type": "Expense",
        "debit": cogs_total,
        "credit": 0.0,
    })

    # Operating Expenses
    items.append({
        "account": "Operating Expenses (Overheads)",
        "type": "Expense",
        "debit": expenses_total,
        "credit": 0.0,
    })

    # Partner Drawings
    items.append({
        "account": "Partner Drawings / Withdrawals",
        "type": "Contra-Equity",
        "debit": drawings_total,
        "credit": 0.0,
    })

    # Accounts Payable
    items.append({
        "account": "Accounts Payable (Supplier Ledger)",
        "type": "Liability",
        "debit": abs(payables_total) if payables_total < 0 else 0.0,
        "credit": payables_total if payables_total >= 0 else 0.0,
    })

    # Sales Revenue
    items.append({
        "account": "Wholesale Sales Revenue",
        "type": "Revenue",
        "debit": 0.0,
        "credit": revenue_total,
    })

    # Partners Capital
    items.append({
        "account": "Partners Capital (Contributed Equity)",
        "type": "Equity",
        "debit": 0.0,
        "credit": capital_total,
    })

    total_debit = sum(i["debit"] for i in items)
    total_credit = sum(i["credit"] for i in items)
    difference = abs(total_debit - total_credit)
    is_balanced = difference < 0.01

    return render_template(
        "reports/trial_balance.html",
        items=items,
        total_debit=total_debit,
        total_credit=total_credit,
        difference=difference,
        is_balanced=is_balanced,
    )


# ================= 3. PROFIT & LOSS STATEMENT =================
@reports_bp.route("/reports/profit-loss")
@login_required
def profit_loss():
    # Revenue
    total_sales = (
        db.session.query(func.coalesce(func.sum(Sale.total_sale), 0.0)).scalar()
        or 0.0
    )
    # COGS
    total_cogs = (
        db.session.query(func.coalesce(func.sum(Sale.total_cost), 0.0)).scalar()
        or 0.0
    )
    gross_profit = total_sales - total_cogs
    gross_margin = (gross_profit / total_sales * 100.0) if total_sales > 0 else 0.0

    # Expense breakdown by category
    cat_expenses = (
        db.session.query(
            Expense.category, func.coalesce(func.sum(Expense.amount), 0.0)
        )
        .group_by(Expense.category)
        .order_by(func.sum(Expense.amount).desc())
        .all()
    )
    total_expenses = sum(c[1] for c in cat_expenses)

    net_profit = gross_profit - total_expenses
    net_margin = (net_profit / total_sales * 100.0) if total_sales > 0 else 0.0

    # Partners
    partners = Partner.query.order_by(Partner.id.asc()).all()
    partner_shares = []
    for p in partners:
        share = net_profit * (p.profit_share_percentage / 100.0)
        partner_shares.append({
            "partner": p,
            "share": share,
        })

    return render_template(
        "reports/profit_loss.html",
        total_sales=total_sales,
        total_cogs=total_cogs,
        gross_profit=gross_profit,
        gross_margin=gross_margin,
        cat_expenses=cat_expenses,
        total_expenses=total_expenses,
        net_profit=net_profit,
        net_margin=net_margin,
        partner_shares=partner_shares,
    )


# ================= 4. BALANCE SHEET =================
@reports_bp.route("/reports/balance-sheet")
@login_required
def balance_sheet():
    # Assets
    cash_balance = (
        db.session.query(func.coalesce(func.sum(Account.balance), 0.0))
        .filter(Account.account_type == "Cash")
        .scalar()
        or 0.0
    )
    bank_balance = (
        db.session.query(func.coalesce(func.sum(Account.balance), 0.0))
        .filter(Account.account_type == "Bank")
        .scalar()
        or 0.0
    )
    receivables = (
        db.session.query(func.coalesce(func.sum(Customer.current_balance), 0.0)).scalar()
        or 0.0
    )
    inventory = (
        db.session.query(
            func.coalesce(func.sum(Product.current_stock * Product.cost_price), 0.0)
        ).scalar()
        or 0.0
    )
    total_assets = cash_balance + bank_balance + receivables + inventory

    # Liabilities
    payables = (
        db.session.query(func.coalesce(func.sum(Supplier.current_balance), 0.0)).scalar()
        or 0.0
    )
    total_liabilities = payables

    # Equity
    contributed_capital = (
        db.session.query(func.coalesce(func.sum(Partner.capital_balance), 0.0)).scalar()
        or 0.0
    )
    total_sales = (
        db.session.query(func.coalesce(func.sum(Sale.total_sale), 0.0)).scalar()
        or 0.0
    )
    total_cogs = (
        db.session.query(func.coalesce(func.sum(Sale.total_cost), 0.0)).scalar()
        or 0.0
    )
    total_expenses = (
        db.session.query(func.coalesce(func.sum(Expense.amount), 0.0)).scalar()
        or 0.0
    )
    retained_profit = (total_sales - total_cogs) - total_expenses
    drawings = (
        db.session.query(func.coalesce(func.sum(PartnerDrawing.amount), 0.0)).scalar()
        or 0.0
    )

    total_equity = contributed_capital + retained_profit - drawings
    total_liabilities_and_equity = total_liabilities + total_equity

    return render_template(
        "reports/balance_sheet.html",
        cash_balance=cash_balance,
        bank_balance=bank_balance,
        receivables=receivables,
        inventory=inventory,
        total_assets=total_assets,
        payables=payables,
        total_liabilities=total_liabilities,
        contributed_capital=contributed_capital,
        retained_profit=retained_profit,
        drawings=drawings,
        total_equity=total_equity,
        total_liabilities_and_equity=total_liabilities_and_equity,
    )
