from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy import func
from app import db
from models.expense import Expense
from models.cash_bank import Account, CashBankTransaction

expenses_bp = Blueprint("expenses", __name__)

DEFAULT_CATEGORIES = [
    "Shop Rent",
    "Electricity Bill",
    "Labor & Wages",
    "Tea & Refreshment",
    "Freight & Carriage",
    "Packaging Material",
    "Shop Maintenance",
    "Printing & Stationery",
    "Marketing & Travel",
    "General Office Expense",
    "Other Miscellaneous",
]


@expenses_bp.route("/expenses")
@login_required
def expenses_list():
    category_filter = request.args.get("category", "").strip()
    search = request.args.get("search", "").strip()
    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()

    query = Expense.query

    if category_filter:
        query = query.filter_by(category=category_filter)
    if search:
        query = query.filter(
            (Expense.title.ilike(f"%{search}%"))
            | (Expense.description.ilike(f"%{search}%"))
            | (Expense.payee.ilike(f"%{search}%"))
            | (Expense.expense_no.ilike(f"%{search}%"))
        )
    if start_date:
        try:
            s_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Expense.date >= s_dt)
        except ValueError:
            pass
    if end_date:
        try:
            e_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(
                hour=23, minute=59, second=59
            )
            query = query.filter(Expense.date <= e_dt)
        except ValueError:
            pass

    expenses = query.order_by(Expense.date.desc(), Expense.id.desc()).all()

    # KPI Metrics
    total_expenses = (
        db.session.query(func.coalesce(func.sum(Expense.amount), 0.0)).scalar() or 0.0
    )

    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)
    this_month_expenses = (
        db.session.query(func.coalesce(func.sum(Expense.amount), 0.0))
        .filter(Expense.date >= month_start)
        .scalar()
        or 0.0
    )

    cash_expenses = (
        db.session.query(func.coalesce(func.sum(Expense.amount), 0.0))
        .join(Account, Expense.account_id == Account.id, isouter=True)
        .filter((Expense.payment_method == "Cash") | (Account.account_type == "Cash"))
        .scalar()
        or 0.0
    )

    bank_expenses = (
        db.session.query(func.coalesce(func.sum(Expense.amount), 0.0))
        .join(Account, Expense.account_id == Account.id)
        .filter(Account.account_type == "Bank")
        .scalar()
        or 0.0
    )

    # Categories list for dropdown
    existing_categories = [
        r[0]
        for r in db.session.query(Expense.category).distinct().all()
        if r[0]
    ]
    all_categories = sorted(list(set(DEFAULT_CATEGORIES + existing_categories)))

    return render_template(
        "expenses/index.html",
        expenses=expenses,
        total_expenses=total_expenses,
        this_month_expenses=this_month_expenses,
        cash_expenses=cash_expenses,
        bank_expenses=bank_expenses,
        all_categories=all_categories,
        category_filter=category_filter,
        search=search,
        start_date=start_date,
        end_date=end_date,
    )


@expenses_bp.route("/expenses/new", methods=["GET", "POST"])
@login_required
def expense_new():
    accounts = Account.query.order_by(Account.account_name.asc()).all()
    existing_categories = [
        r[0]
        for r in db.session.query(Expense.category).distinct().all()
        if r[0]
    ]
    all_categories = sorted(list(set(DEFAULT_CATEGORIES + existing_categories)))

    if request.method == "POST":
        date_str = request.form.get("date", "").strip()
        category = request.form.get("category", "").strip()
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        payee = request.form.get("payee", "").strip()
        amount_raw = request.form.get("amount", "0").strip()
        account_id_raw = request.form.get("account_id", "").strip()
        reference = request.form.get("reference", "").strip()

        try:
            amount = float(amount_raw)
        except ValueError:
            amount = 0.0

        if not category:
            flash("Please specify an Expense Head / Category.", "danger")
            return redirect(url_for("expenses.expense_new"))

        if not title:
            title = category

        if amount <= 0:
            flash("Expense amount must be greater than zero.", "danger")
            return redirect(url_for("expenses.expense_new"))

        try:
            expense_date = (
                datetime.strptime(date_str, "%Y-%m-%d")
                if date_str
                else datetime.utcnow()
            )
        except ValueError:
            expense_date = datetime.utcnow()

        # Generate sequential expense number
        last_expense = Expense.query.order_by(Expense.id.desc()).first()
        next_num = (last_expense.id + 1) if last_expense else 1
        expense_no = f"EXP-{next_num:04d}"

        account = None
        payment_method = "Cash"
        if account_id_raw:
            try:
                account = db.session.get(Account, int(account_id_raw))
                if account:
                    payment_method = account.account_type
            except (ValueError, TypeError):
                pass

        expense = Expense(
            expense_no=expense_no,
            date=expense_date,
            category=category,
            title=title,
            description=description,
            payee=payee,
            amount=amount,
            payment_method=payment_method,
            account_id=account.id if account else None,
            reference=reference,
        )
        db.session.add(expense)
        db.session.flush()

        # Accounting connection: deduct from selected cash or bank account
        if account:
            account.balance = (account.balance or 0.0) - amount
            cb_tx = CashBankTransaction(
                account_id=account.id,
                date=expense_date,
                transaction_type="Expense",
                amount=amount,
                reference_type="Expense",
                reference_id=expense.id,
                description=f"Expense #{expense_no}: {title} ({category})"
                + (f" - Payee: {payee}" if payee else ""),
            )
            db.session.add(cb_tx)

        db.session.commit()
        flash(
            f"Expense voucher #{expense_no} for PKR {amount:,.2f} recorded successfully.",
            "success",
        )
        return redirect(url_for("expenses.expenses_list"))

    return render_template(
        "expenses/new.html",
        accounts=accounts,
        all_categories=all_categories,
        today=datetime.utcnow().strftime("%Y-%m-%d"),
    )


@expenses_bp.route("/expenses/<int:id>")
@login_required
def expense_voucher(id):
    expense = db.session.get(Expense, id)
    if not expense:
        flash("Expense voucher not found.", "danger")
        return redirect(url_for("expenses.expenses_list"))
    return render_template("expenses/voucher.html", expense=expense)
