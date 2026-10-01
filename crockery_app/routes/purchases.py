from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from models.purchase import Purchase, PurchaseItem
from models.product import Product
from models.supplier import Supplier
from models.stock import StockMovement
from models.cash_bank import Account, CashBankTransaction

purchases_bp = Blueprint("purchases", __name__)


@purchases_bp.route("/purchases")
@login_required
def purchases_list():
    status_filter = request.args.get("status", "").strip()
    search = request.args.get("search", "").strip()

    query = Purchase.query
    if status_filter:
        query = query.filter_by(payment_status=status_filter)
    if search:
        query = query.join(Supplier).filter(
            (Purchase.bill_no.ilike(f"%{search}%")) | (Supplier.name.ilike(f"%{search}%"))
        )

    purchases = query.order_by(Purchase.date.desc(), Purchase.id.desc()).all()
    return render_template(
        "purchases/index.html", purchases=purchases, status_filter=status_filter, search=search
    )


@purchases_bp.route("/purchases/new", methods=["GET", "POST"])
@login_required
def purchase_new():
    suppliers = Supplier.query.filter_by(is_active=True).order_by(Supplier.name.asc()).all()
    products = Product.query.filter_by(is_active=True).order_by(Product.name.asc()).all()
    accounts = Account.query.order_by(Account.account_name.asc()).all()

    if request.method == "POST":
        bill_no = request.form.get("bill_no", "").strip()
        date_str = request.form.get("date", "").strip()
        supplier_id = request.form.get("supplier_id")
        paid_amount = float(request.form.get("paid_amount", 0.0) or 0.0)
        account_id = request.form.get("account_id")
        notes = request.form.get("notes", "").strip()

        # Parse date
        try:
            purchase_date = (
                datetime.strptime(date_str, "%Y-%m-%d")
                if date_str
                else datetime.utcnow()
            )
        except ValueError:
            purchase_date = datetime.utcnow()

        if not bill_no:
            # Auto-generate bill_no if not provided
            last_p = Purchase.query.order_by(Purchase.id.desc()).first()
            next_num = (last_p.id + 1) if last_p else 1
            bill_no = f"R-{next_num:03d}"

        if not supplier_id:
            flash("Please select a supplier.", "danger")
            return redirect(url_for("purchases.purchase_new"))

        if Purchase.query.filter_by(bill_no=bill_no).first():
            flash(f"Bill No '{bill_no}' already exists.", "danger")
            return redirect(url_for("purchases.purchase_new"))

        # Process Line Items
        product_ids = request.form.getlist("product_id[]")
        quantities = request.form.getlist("quantity[]")
        units = request.form.getlist("unit[]")
        rates = request.form.getlist("rate[]")

        if not product_ids or len(product_ids) == 0:
            flash("Please add at least one item to this purchase.", "danger")
            return redirect(url_for("purchases.purchase_new"))

        total_amount = 0.0
        line_items_data = []

        for p_id, q_val, u_val, r_val in zip(product_ids, quantities, units, rates):
            if not p_id:
                continue
            qty = float(q_val or 0.0)
            rate = float(r_val or 0.0)
            line_total = qty * rate
            total_amount += line_total
            line_items_data.append({
                "product_id": int(p_id),
                "quantity": qty,
                "unit": u_val,
                "unit_price": rate,
                "total_price": line_total,
            })

        balance_amount = max(0.0, total_amount - paid_amount)
        if balance_amount == 0.0:
            payment_status = "Paid"
        elif paid_amount > 0.0:
            payment_status = "Partial"
        else:
            payment_status = "Unpaid"

        # 1. Create Purchase Record
        purchase = Purchase(
            bill_no=bill_no,
            supplier_id=int(supplier_id),
            date=purchase_date,
            total_amount=total_amount,
            paid_amount=paid_amount,
            balance_amount=balance_amount,
            payment_status=payment_status,
            notes=notes,
        )
        db.session.add(purchase)
        db.session.flush()  # assign purchase.id

        # 2. Stock Connection: Add Purchase Items, Increase Stock & Log StockMovement
        for item in line_items_data:
            p_item = PurchaseItem(
                purchase_id=purchase.id,
                product_id=item["product_id"],
                quantity=item["quantity"],
                unit=item["unit"],
                unit_price=item["unit_price"],
                total_price=item["total_price"],
            )
            db.session.add(p_item)

            prod = db.session.get(Product, item["product_id"])
            if prod:
                prod.current_stock += item["quantity"]
                prod.cost_price = item["unit_price"]  # update latest cost
                stock_mov = StockMovement(
                    product_id=prod.id,
                    date=purchase_date,
                    movement_type="IN",
                    quantity=item["quantity"],
                    unit_cost=item["unit_price"],
                    reference_type="Purchase",
                    reference_id=purchase.id,
                    notes=f"Purchase Bill: {purchase.bill_no}",
                )
                db.session.add(stock_mov)

        # 3. Supplier Ledger Connection: Update Supplier Balance (Payable)
        supplier = db.session.get(Supplier, int(supplier_id))
        if supplier:
            supplier.current_balance += balance_amount

        # 4. Cash/Bank Connection: Deduct Paid Amount and Record Transaction
        if paid_amount > 0 and account_id:
            account = db.session.get(Account, int(account_id))
            if account:
                account.balance -= paid_amount
                c_txn = CashBankTransaction(
                    date=purchase_date,
                    transaction_type="Supplier Payment",
                    account_id=account.id,
                    amount=paid_amount,
                    reference_type="Purchase",
                    reference_id=purchase.id,
                    description=f"Payment for Bill {purchase.bill_no} ({supplier.name})",
                )
                db.session.add(c_txn)

        db.session.commit()
        flash(f"Purchase Bill '{purchase.bill_no}' recorded successfully. Stock and Supplier balance updated!", "success")
        return redirect(url_for("purchases.purchase_view", id=purchase.id))

    # Auto-generate suggestion for next bill no
    last_p = Purchase.query.order_by(Purchase.id.desc()).first()
    next_bill_no = f"R-{(last_p.id + 1):03d}" if last_p else "R-001"
    today_date = datetime.utcnow().strftime("%Y-%m-%d")

    return render_template(
        "purchases/new.html",
        suppliers=suppliers,
        products=products,
        accounts=accounts,
        next_bill_no=next_bill_no,
        today_date=today_date,
    )


@purchases_bp.route("/purchases/<int:id>")
@login_required
def purchase_view(id):
    purchase = db.session.get(Purchase, id)
    if not purchase:
        flash("Purchase record not found.", "danger")
        return redirect(url_for("purchases.purchases_list"))
    return render_template("purchases/view.html", purchase=purchase)
