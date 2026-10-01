from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from models.sale import Sale, SaleItem
from models.product import Product
from models.customer import Customer
from models.stock import StockMovement
from models.cash_bank import Account, CashBankTransaction

sales_bp = Blueprint("sales", __name__)


@sales_bp.route("/sales")
@login_required
def sales_list():
    status_filter = request.args.get("status", "").strip()
    search = request.args.get("search", "").strip()

    query = Sale.query
    if status_filter:
        query = query.filter_by(payment_status=status_filter)
    if search:
        query = query.join(Customer).filter(
            (Sale.invoice_no.ilike(f"%{search}%")) | (Customer.name.ilike(f"%{search}%"))
        )

    sales = query.order_by(Sale.date.desc(), Sale.id.desc()).all()

    total_sales_amount = sum(s.total_sale for s in sales)
    total_cost_amount = sum(s.total_cost for s in sales)
    total_gross_profit = sum(s.gross_profit for s in sales)
    total_received = sum(s.received_amount for s in sales)
    total_balance = sum(s.balance_amount for s in sales)

    summary = {
        "total_sales": total_sales_amount,
        "total_cost": total_cost_amount,
        "total_gross_profit": total_gross_profit,
        "total_received": total_received,
        "total_balance": total_balance,
    }

    return render_template(
        "sales/index.html",
        sales=sales,
        summary=summary,
        status_filter=status_filter,
        search=search,
    )


@sales_bp.route("/sales/new", methods=["GET", "POST"])
@login_required
def sale_new():
    customers = Customer.query.filter_by(is_active=True).order_by(Customer.name.asc()).all()
    products = Product.query.filter_by(is_active=True).order_by(Product.name.asc()).all()
    accounts = Account.query.order_by(Account.account_name.asc()).all()

    if request.method == "POST":
        invoice_no = request.form.get("invoice_no", "").strip()
        date_str = request.form.get("date", "").strip()
        customer_id = request.form.get("customer_id")
        received_amount = float(request.form.get("received_amount", 0.0) or 0.0)
        account_id = request.form.get("account_id")
        notes = request.form.get("notes", "").strip()

        try:
            sale_date = (
                datetime.strptime(date_str, "%Y-%m-%d")
                if date_str
                else datetime.utcnow()
            )
        except ValueError:
            sale_date = datetime.utcnow()

        if not invoice_no:
            last_s = Sale.query.order_by(Sale.id.desc()).first()
            next_num = (last_s.id + 1) if last_s else 1
            invoice_no = f"INV-{next_num:03d}"

        if not customer_id:
            flash("Please select a customer.", "danger")
            return redirect(url_for("sales.sale_new"))

        if Sale.query.filter_by(invoice_no=invoice_no).first():
            flash(f"Invoice No '{invoice_no}' already exists.", "danger")
            return redirect(url_for("sales.sale_new"))

        # Process Line Items
        product_ids = request.form.getlist("product_id[]")
        quantities = request.form.getlist("quantity[]")
        units = request.form.getlist("unit[]")
        cost_rates = request.form.getlist("cost_rate[]")
        sale_rates = request.form.getlist("sale_rate[]")

        if not product_ids or len(product_ids) == 0:
            flash("Please add at least one product to this invoice.", "danger")
            return redirect(url_for("sales.sale_new"))

        total_cost = 0.0
        total_sale = 0.0
        line_items_data = []

        # Validate Stock & Prepare Items
        stock_errors = []
        for p_id, q_val, u_val, c_val, s_val in zip(product_ids, quantities, units, cost_rates, sale_rates):
            if not p_id:
                continue
            prod = db.session.get(Product, int(p_id))
            qty = float(q_val or 0.0)
            cost_r = float(c_val or (prod.cost_price if prod else 0.0))
            sale_r = float(s_val or (prod.sale_price if prod else 0.0))

            if prod and qty > prod.current_stock:
                stock_errors.append(f"Insufficient stock for '{prod.name}' (Available: {prod.current_stock}, Requested: {qty})")

            c_total = qty * cost_r
            s_total = qty * sale_r
            profit = s_total - c_total

            total_cost += c_total
            total_sale += s_total

            line_items_data.append({
                "product_id": int(p_id),
                "quantity": qty,
                "unit": u_val or (prod.unit if prod else "Pcs"),
                "cost_rate": cost_r,
                "sale_rate": sale_r,
                "cost_total": c_total,
                "sale_total": s_total,
                "profit": profit,
            })

        if stock_errors:
            for err in stock_errors:
                flash(err, "warning")

        gross_profit = total_sale - total_cost
        balance_amount = max(0.0, total_sale - received_amount)

        if balance_amount == 0.0:
            payment_status = "Paid"
        elif received_amount > 0.0:
            payment_status = "Partial"
        else:
            payment_status = "Unpaid"

        # 1. Create Sale Record
        sale = Sale(
            invoice_no=invoice_no,
            customer_id=int(customer_id),
            date=sale_date,
            total_cost=total_cost,
            total_sale=total_sale,
            gross_profit=gross_profit,
            received_amount=received_amount,
            balance_amount=balance_amount,
            payment_status=payment_status,
            notes=notes,
        )
        db.session.add(sale)
        db.session.flush()

        # 2. Add Sale Items, Decrease Stock & Log StockMovement (OUT)
        for item in line_items_data:
            s_item = SaleItem(
                sale_id=sale.id,
                product_id=item["product_id"],
                quantity=item["quantity"],
                unit=item["unit"],
                cost_rate=item["cost_rate"],
                sale_rate=item["sale_rate"],
                cost_total=item["cost_total"],
                sale_total=item["sale_total"],
                profit=item["profit"],
            )
            db.session.add(s_item)

            prod = db.session.get(Product, item["product_id"])
            if prod:
                prod.current_stock -= item["quantity"]

                stock_mov = StockMovement(
                    product_id=prod.id,
                    date=sale_date,
                    movement_type="OUT",
                    quantity=item["quantity"],
                    unit_cost=item["cost_rate"],
                    reference_type="Sale",
                    reference_id=sale.id,
                    notes=f"Sale Invoice: {sale.invoice_no}",
                )
                db.session.add(stock_mov)

        # 3. Customer Ledger Connection: Update Customer Receivable Balance
        customer = db.session.get(Customer, int(customer_id))
        if customer:
            customer.current_balance += balance_amount

        # 4. Cash/Bank Connection: Deposit Received Amount and Log Transaction
        if received_amount > 0 and account_id:
            account = db.session.get(Account, int(account_id))
            if account:
                account.balance += received_amount
                c_txn = CashBankTransaction(
                    date=sale_date,
                    transaction_type="Customer Receipt",
                    account_id=account.id,
                    amount=received_amount,
                    reference_type="Sale",
                    reference_id=sale.id,
                    description=f"Receipt for Invoice {sale.invoice_no} ({customer.name})",
                )
                db.session.add(c_txn)

        db.session.commit()
        flash(
            f"Sales Invoice '{sale.invoice_no}' created successfully! Stock reduced and Customer balance updated.",
            "success",
        )
        return redirect(url_for("sales.sale_view", id=sale.id))

    # Auto-generate suggestion for next invoice no
    last_s = Sale.query.order_by(Sale.id.desc()).first()
    next_invoice_no = f"INV-{(last_s.id + 1):03d}" if last_s else "INV-001"
    today_date = datetime.utcnow().strftime("%Y-%m-%d")

    return render_template(
        "sales/new.html",
        customers=customers,
        products=products,
        accounts=accounts,
        next_invoice_no=next_invoice_no,
        today_date=today_date,
    )


@sales_bp.route("/sales/<int:id>")
@login_required
def sale_view(id):
    sale = db.session.get(Sale, id)
    if not sale:
        flash("Sales invoice not found.", "danger")
        return redirect(url_for("sales.sales_list"))
    return render_template("sales/view.html", sale=sale)
