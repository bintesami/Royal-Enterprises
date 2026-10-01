from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy import func
from app import db
from models.product import Product
from models.stock import StockMovement

stock_bp = Blueprint("stock", __name__)


@stock_bp.route("/stock")
@login_required
def stock_list():
    search = request.args.get("search", "").strip()
    low_stock_only = request.args.get("low_stock", "") == "1"
    out_of_stock_only = request.args.get("out_of_stock", "") == "1"

    query = Product.query
    if search:
        query = query.filter(
            (Product.name.ilike(f"%{search}%")) | (Product.code.ilike(f"%{search}%"))
        )
    if low_stock_only:
        query = query.filter(Product.current_stock <= Product.min_stock_alert)
    if out_of_stock_only:
        query = query.filter(Product.current_stock <= 0)

    products = query.order_by(Product.code.asc()).all()

    # Calculate live inventory statistics
    total_products = Product.query.count()
    total_quantity = (
        db.session.query(func.coalesce(func.sum(Product.current_stock), 0.0)).scalar()
        or 0.0
    )
    total_stock_value = (
        db.session.query(
            func.coalesce(func.sum(Product.current_stock * Product.cost_price), 0.0)
        ).scalar()
        or 0.0
    )
    low_stock_count = Product.query.filter(
        Product.current_stock <= Product.min_stock_alert
    ).count()
    out_of_stock_count = Product.query.filter(Product.current_stock <= 0).count()

    stats = {
        "total_products": total_products,
        "total_quantity": total_quantity,
        "total_stock_value": total_stock_value,
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock_count,
    }

    return render_template(
        "stock/index.html",
        products=products,
        stats=stats,
        search=search,
        low_stock_only=low_stock_only,
        out_of_stock_only=out_of_stock_only,
    )


@stock_bp.route("/stock/ledger")
@login_required
def stock_ledger():
    product_id_raw = request.args.get("product_id", "").strip()
    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()

    products = Product.query.order_by(Product.name.asc()).all()
    selected_product = None

    query = StockMovement.query

    if product_id_raw:
        try:
            pid = int(product_id_raw)
            query = query.filter_by(product_id=pid)
            selected_product = db.session.get(Product, pid)
        except ValueError:
            pass

    if start_date:
        try:
            s_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(StockMovement.date >= s_dt)
        except ValueError:
            pass

    if end_date:
        try:
            e_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(
                hour=23, minute=59, second=59
            )
            query = query.filter(StockMovement.date <= e_dt)
        except ValueError:
            pass

    movements = query.order_by(
        StockMovement.date.asc(), StockMovement.id.asc()
    ).all()

    # Calculate line-by-line running balance
    ledger_entries = []
    running_balance = 0.0

    for m in movements:
        # Determine In vs Out
        qty_in = 0.0
        qty_out = 0.0
        rate = m.unit_cost or 0.0

        if m.movement_type == "IN":
            qty_in = m.quantity
            running_balance += m.quantity
        elif m.movement_type == "OUT":
            qty_out = m.quantity
            running_balance -= m.quantity
        else:  # ADJUSTMENT
            if m.quantity >= 0:
                qty_in = m.quantity
                running_balance += m.quantity
            else:
                qty_out = abs(m.quantity)
                running_balance -= abs(m.quantity)

        val = running_balance * rate

        ref_display = f"{m.reference_type or 'DOC'} #{m.reference_id or m.id}"

        ledger_entries.append({
            "id": m.id,
            "date": m.date,
            "product": m.product,
            "reference": ref_display,
            "type": m.movement_type,
            "notes": m.notes,
            "qty_in": qty_in,
            "qty_out": qty_out,
            "balance": running_balance,
            "rate": rate,
            "value": val,
        })

    total_in = sum(e["qty_in"] for e in ledger_entries)
    total_out = sum(e["qty_out"] for e in ledger_entries)

    return render_template(
        "stock/ledger.html",
        products=products,
        selected_product=selected_product,
        entries=ledger_entries,
        total_in=total_in,
        total_out=total_out,
        final_balance=running_balance,
        product_id=product_id_raw,
        start_date=start_date,
        end_date=end_date,
    )


@stock_bp.route("/stock/adjustments/new", methods=["GET", "POST"])
@login_required
def stock_adjustment_new():
    products = Product.query.filter_by(is_active=True).order_by(Product.name.asc()).all()

    if request.method == "POST":
        product_id = request.form.get("product_id")
        date_str = request.form.get("date", "").strip()
        adj_type = request.form.get("adjustment_type", "Decrease")
        qty_raw = request.form.get("quantity", "0").strip()
        reason = request.form.get("reason", "Damage / Breakage").strip()
        notes = request.form.get("notes", "").strip()

        try:
            qty = float(qty_raw)
        except ValueError:
            qty = 0.0

        if not product_id:
            flash("Please select a product to adjust.", "danger")
            return redirect(url_for("stock.stock_adjustment_new"))

        product = db.session.get(Product, int(product_id))
        if not product:
            flash("Product not found.", "danger")
            return redirect(url_for("stock.stock_adjustment_new"))

        if qty <= 0:
            flash("Adjustment quantity must be greater than zero.", "danger")
            return redirect(url_for("stock.stock_adjustment_new"))

        try:
            adj_date = (
                datetime.strptime(date_str, "%Y-%m-%d")
                if date_str
                else datetime.utcnow()
            )
        except ValueError:
            adj_date = datetime.utcnow()

        # Update stock
        if adj_type == "Increase":
            product.current_stock = (product.current_stock or 0.0) + qty
            movement = StockMovement(
                product_id=product.id,
                date=adj_date,
                movement_type="IN",
                quantity=qty,
                unit_cost=product.cost_price or 0.0,
                reference_type="Adjustment",
                notes=f"Stock Audit Increase ({reason}): {notes}",
            )
        else:  # Decrease (Damage/Breakage)
            product.current_stock = (product.current_stock or 0.0) - qty
            movement = StockMovement(
                product_id=product.id,
                date=adj_date,
                movement_type="OUT",
                quantity=qty,
                unit_cost=product.cost_price or 0.0,
                reference_type="Adjustment",
                notes=f"Stock Deduction ({reason}): {notes}",
            )

        db.session.add(movement)
        db.session.commit()

        flash(
            f"Stock for '{product.name}' adjusted by {qty:g} {product.unit} ({adj_type}). New stock: {product.current_stock:g} {product.unit}.",
            "success",
        )
        return redirect(url_for("stock.stock_list"))

    return render_template(
        "stock/adjustment_new.html",
        products=products,
        today=datetime.utcnow().strftime("%Y-%m-%d"),
    )
