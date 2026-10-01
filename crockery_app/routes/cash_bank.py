from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from models.cash_bank import Account, CashBankTransaction
from models.customer import Customer
from models.supplier import Supplier

cash_bank_bp = Blueprint("cash_bank", __name__)


# ================= CASH & BANK BOOK =================
@cash_bank_bp.route("/cash-bank")
@login_required
def cash_bank_book():
    account_filter = request.args.get("account_id")
    type_filter = request.args.get("type", "").strip()

    accounts = Account.query.order_by(Account.account_name.asc()).all()

    query = CashBankTransaction.query
    selected_account = None
    if account_filter:
        selected_account = db.session.get(Account, int(account_filter))
        query = query.filter_by(account_id=int(account_filter))
    if type_filter:
        query = query.filter_by(transaction_type=type_filter)

    # Order chronologically for running balance calculation
    transactions = query.order_by(CashBankTransaction.date.asc(), CashBankTransaction.id.asc()).all()

    # Calculate Cash and Bank Balances
    total_cash = sum(a.balance for a in accounts if a.account_type == "Cash")
    total_bank = sum(a.balance for a in accounts if a.account_type == "Bank")
    total_liquidity = total_cash + total_bank

    # Prepare rows matching Excel Cash & Bank Book columns:
    # Date | Type | Description | Reference | Cash In | Cash Out | Bank In | Bank Out | Running Balance
    book_entries = []
    running_balance = 0.0

    for txn in transactions:
        is_cash = txn.account.account_type == "Cash" if txn.account else True
        is_inflow = txn.transaction_type in ("Customer Receipt", "Transfer In", "Deposit", "Capital")

        cash_in = txn.amount if (is_cash and is_inflow) else 0.0
        cash_out = txn.amount if (is_cash and not is_inflow) else 0.0
        bank_in = txn.amount if (not is_cash and is_inflow) else 0.0
        bank_out = txn.amount if (not is_cash and not is_inflow) else 0.0

        if is_inflow:
            running_balance += txn.amount
        else:
            running_balance -= txn.amount

        book_entries.append({
            "id": txn.id,
            "date": txn.date,
            "type": txn.transaction_type,
            "account_name": txn.account.account_name if txn.account else "N/A",
            "description": txn.description or "",
            "reference": f"{txn.reference_type or ''} #{txn.reference_id or ''}".strip(),
            "cash_in": cash_in,
            "cash_out": cash_out,
            "bank_in": bank_in,
            "bank_out": bank_out,
            "balance": running_balance,
        })

    # Reverse for latest first display
    book_entries.reverse()

    stats = {
        "total_cash": total_cash,
        "total_bank": total_bank,
        "total_liquidity": total_liquidity,
        "total_txns": len(transactions),
    }

    return render_template(
        "cash_bank/index.html",
        accounts=accounts,
        selected_account=selected_account,
        book_entries=book_entries,
        stats=stats,
        type_filter=type_filter,
    )


# ================= ACCOUNTS MANAGEMENT =================
@cash_bank_bp.route("/cash-bank/accounts", methods=["GET", "POST"])
@login_required
def accounts_list():
    if request.method == "POST":
        account_name = request.form.get("account_name", "").strip()
        account_type = request.form.get("account_type", "Bank").strip()
        bank_name = request.form.get("bank_name", "").strip()
        account_number = request.form.get("account_number", "").strip()
        opening_balance = float(request.form.get("opening_balance", 0.0) or 0.0)

        if not account_name:
            flash("Account name is required.", "danger")
            return redirect(url_for("cash_bank.accounts_list"))

        account = Account(
            account_name=account_name,
            account_type=account_type,
            bank_name=bank_name,
            account_number=account_number,
            balance=opening_balance,
        )
        db.session.add(account)
        db.session.commit()
        flash(f"Account '{account_name}' created successfully.", "success")
        return redirect(url_for("cash_bank.accounts_list"))

    accounts = Account.query.order_by(Account.account_type.asc(), Account.account_name.asc()).all()
    return render_template("cash_bank/accounts.html", accounts=accounts)


# ================= RECEIVE PAYMENT (CUSTOMER) =================
@cash_bank_bp.route("/cash-bank/receive-payment", methods=["GET", "POST"])
@login_required
def receive_payment():
    customers = Customer.query.order_by(Customer.name.asc()).all()
    accounts = Account.query.order_by(Account.account_name.asc()).all()

    if request.method == "POST":
        customer_id = request.form.get("customer_id")
        account_id = request.form.get("account_id")
        amount = float(request.form.get("amount", 0.0) or 0.0)
        date_str = request.form.get("date", "").strip()
        reference = request.form.get("reference", "").strip()
        notes = request.form.get("notes", "").strip()

        if not customer_id or not account_id or amount <= 0:
            flash("Please specify customer, account, and an amount greater than 0.", "danger")
            return redirect(url_for("cash_bank.receive_payment"))

        try:
            txn_date = datetime.strptime(date_str, "%Y-%m-%d") if date_str else datetime.utcnow()
        except ValueError:
            txn_date = datetime.utcnow()

        customer = db.session.get(Customer, int(customer_id))
        account = db.session.get(Account, int(account_id))

        if not customer or not account:
            flash("Invalid customer or account selected.", "danger")
            return redirect(url_for("cash_bank.receive_payment"))

        # 1. Deposit into Account
        account.balance += amount

        # 2. Reduce Customer Receivable Balance
        customer.current_balance -= amount

        # 3. Log CashBankTransaction
        description = f"Received payment from {customer.name}"
        if notes:
            description += f" - {notes}"

        txn = CashBankTransaction(
            date=txn_date,
            transaction_type="Customer Receipt",
            account_id=account.id,
            amount=amount,
            reference_type="Receipt Voucher",
            reference_id=customer.id,
            description=description,
        )
        db.session.add(txn)
        db.session.commit()

        flash(
            f"Payment of PKR {amount:,.2f} received from '{customer.name}' into '{account.account_name}'. Customer balance updated!",
            "success",
        )
        return redirect(url_for("cash_bank.cash_bank_book"))

    # Prefill customer if passed in query string
    prefill_customer_id = request.args.get("customer_id")
    selected_customer = db.session.get(Customer, int(prefill_customer_id)) if prefill_customer_id else None
    today_date = datetime.utcnow().strftime("%Y-%m-%d")

    return render_template(
        "cash_bank/receive_payment.html",
        customers=customers,
        accounts=accounts,
        selected_customer=selected_customer,
        today_date=today_date,
    )


# ================= MAKE PAYMENT (SUPPLIER) =================
@cash_bank_bp.route("/cash-bank/make-payment", methods=["GET", "POST"])
@login_required
def make_payment():
    suppliers = Supplier.query.order_by(Supplier.name.asc()).all()
    accounts = Account.query.order_by(Account.account_name.asc()).all()

    if request.method == "POST":
        supplier_id = request.form.get("supplier_id")
        account_id = request.form.get("account_id")
        amount = float(request.form.get("amount", 0.0) or 0.0)
        date_str = request.form.get("date", "").strip()
        reference = request.form.get("reference", "").strip()
        notes = request.form.get("notes", "").strip()

        if not supplier_id or not account_id or amount <= 0:
            flash("Please specify supplier, account, and an amount greater than 0.", "danger")
            return redirect(url_for("cash_bank.make_payment"))

        try:
            txn_date = datetime.strptime(date_str, "%Y-%m-%d") if date_str else datetime.utcnow()
        except ValueError:
            txn_date = datetime.utcnow()

        supplier = db.session.get(Supplier, int(supplier_id))
        account = db.session.get(Account, int(account_id))

        if not supplier or not account:
            flash("Invalid supplier or account selected.", "danger")
            return redirect(url_for("cash_bank.make_payment"))

        # 1. Deduct from Account
        account.balance -= amount

        # 2. Reduce Supplier Payable Balance
        supplier.current_balance -= amount

        # 3. Log CashBankTransaction
        description = f"Payment to supplier {supplier.name}"
        if notes:
            description += f" - {notes}"

        txn = CashBankTransaction(
            date=txn_date,
            transaction_type="Supplier Payment",
            account_id=account.id,
            amount=amount,
            reference_type="Payment Voucher",
            reference_id=supplier.id,
            description=description,
        )
        db.session.add(txn)
        db.session.commit()

        flash(
            f"Payment of PKR {amount:,.2f} made to '{supplier.name}' from '{account.account_name}'. Supplier payable updated!",
            "success",
        )
        return redirect(url_for("cash_bank.cash_bank_book"))

    prefill_supplier_id = request.args.get("supplier_id")
    selected_supplier = db.session.get(Supplier, int(prefill_supplier_id)) if prefill_supplier_id else None
    today_date = datetime.utcnow().strftime("%Y-%m-%d")

    return render_template(
        "cash_bank/make_payment.html",
        suppliers=suppliers,
        accounts=accounts,
        selected_supplier=selected_supplier,
        today_date=today_date,
    )


# ================= FUND TRANSFER BETWEEN ACCOUNTS =================
@cash_bank_bp.route("/cash-bank/transfer", methods=["GET", "POST"])
@login_required
def transfer_funds():
    accounts = Account.query.order_by(Account.account_name.asc()).all()

    if request.method == "POST":
        from_acc_id = request.form.get("from_account_id")
        to_acc_id = request.form.get("to_account_id")
        amount = float(request.form.get("amount", 0.0) or 0.0)
        date_str = request.form.get("date", "").strip()
        reference = request.form.get("reference", "").strip()
        notes = request.form.get("notes", "").strip()

        if not from_acc_id or not to_acc_id or from_acc_id == to_acc_id or amount <= 0:
            flash("Please select different source and destination accounts and a valid amount.", "danger")
            return redirect(url_for("cash_bank.transfer_funds"))

        try:
            txn_date = datetime.strptime(date_str, "%Y-%m-%d") if date_str else datetime.utcnow()
        except ValueError:
            txn_date = datetime.utcnow()

        from_acc = db.session.get(Account, int(from_acc_id))
        to_acc = db.session.get(Account, int(to_acc_id))

        if not from_acc or not to_acc:
            flash("Invalid account selected.", "danger")
            return redirect(url_for("cash_bank.transfer_funds"))

        # Deduct from source and add to destination
        from_acc.balance -= amount
        to_acc.balance += amount

        # Log both legs
        desc_out = f"Transfer to {to_acc.account_name}"
        desc_in = f"Transfer from {from_acc.account_name}"
        if notes:
            desc_out += f" ({notes})"
            desc_in += f" ({notes})"

        txn_out = CashBankTransaction(
            date=txn_date,
            transaction_type="Transfer Out",
            account_id=from_acc.id,
            amount=amount,
            reference_type="Fund Transfer",
            description=desc_out,
        )
        txn_in = CashBankTransaction(
            date=txn_date,
            transaction_type="Transfer In",
            account_id=to_acc.id,
            amount=amount,
            reference_type="Fund Transfer",
            description=desc_in,
        )

        db.session.add_all([txn_out, txn_in])
        db.session.commit()

        flash(
            f"Successfully transferred PKR {amount:,.2f} from '{from_acc.account_name}' to '{to_acc.account_name}'.",
            "success",
        )
        return redirect(url_for("cash_bank.cash_bank_book"))

    today_date = datetime.utcnow().strftime("%Y-%m-%d")
    return render_template("cash_bank/transfer.html", accounts=accounts, today_date=today_date)
