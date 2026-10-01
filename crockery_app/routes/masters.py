from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from models.product import Product
from models.supplier import Supplier
from models.customer import Customer
from models.partner import Partner

masters_bp = Blueprint("masters", __name__)

# ================= PRODUCTS MASTER =================
@masters_bp.route("/products", methods=["GET", "POST"])
@login_required
def products_list():
    if request.method == "POST":
        action = request.form.get("action", "add")
        if action == "add":
            code = request.form.get("code", "").strip()
            name = request.form.get("name", "").strip()
            category = request.form.get("category", "").strip()
            unit = request.form.get("unit", "Pcs").strip()
            cost_price = float(request.form.get("cost_price", 0) or 0)
            sale_price = float(request.form.get("sale_price", 0) or 0)
            opening_stock = float(request.form.get("opening_stock", 0) or 0)
            min_stock_alert = float(request.form.get("min_stock_alert", 10) or 10)

            if not code or not name:
                flash("Product Code and Name are required.", "danger")
                return redirect(url_for("masters.products_list"))

            if Product.query.filter_by(code=code).first():
                flash(f"Product with code '{code}' already exists.", "danger")
                return redirect(url_for("masters.products_list"))

            product = Product(
                code=code,
                name=name,
                category=category,
                unit=unit,
                cost_price=cost_price,
                sale_price=sale_price,
                current_stock=opening_stock,
                min_stock_alert=min_stock_alert,
                is_active=True,
            )
            db.session.add(product)
            db.session.commit()
            flash(f"Product '{name}' added successfully.", "success")
            return redirect(url_for("masters.products_list"))

        elif action == "edit":
            prod_id = request.form.get("product_id")
            product = db.session.get(Product, int(prod_id))
            if product:
                product.name = request.form.get("name", "").strip()
                product.category = request.form.get("category", "").strip()
                product.unit = request.form.get("unit", "Pcs").strip()
                product.cost_price = float(request.form.get("cost_price", 0) or 0)
                product.sale_price = float(request.form.get("sale_price", 0) or 0)
                product.min_stock_alert = float(request.form.get("min_stock_alert", 10) or 10)
                db.session.commit()
                flash(f"Product '{product.name}' updated.", "success")
            return redirect(url_for("masters.products_list"))

    # Search & Filter
    search = request.args.get("search", "").strip()
    query = Product.query
    if search:
        query = query.filter((Product.name.ilike(f"%{search}%")) | (Product.code.ilike(f"%{search}%")))
    products = query.order_by(Product.code.asc()).all()
    return render_template("masters/products.html", products=products, search=search)


@masters_bp.route("/products/toggle/<int:id>", methods=["POST"])
@login_required
def product_toggle(id):
    product = db.session.get(Product, id)
    if product:
        product.is_active = not product.is_active
        db.session.commit()
        status = "activated" if product.is_active else "deactivated"
        flash(f"Product '{product.name}' {status}.", "info")
    return redirect(url_for("masters.products_list"))


# ================= SUPPLIERS MASTER =================
@masters_bp.route("/suppliers", methods=["GET", "POST"])
@login_required
def suppliers_list():
    if request.method == "POST":
        action = request.form.get("action", "add")
        if action == "add":
            name = request.form.get("name", "").strip()
            phone = request.form.get("phone", "").strip()
            address = request.form.get("address", "").strip()
            city = request.form.get("city", "").strip()
            opening_balance = float(request.form.get("opening_balance", 0) or 0)

            if not name:
                flash("Supplier Name is required.", "danger")
                return redirect(url_for("masters.suppliers_list"))

            supplier = Supplier(
                name=name,
                phone=phone,
                address=address,
                city=city,
                opening_balance=opening_balance,
                current_balance=opening_balance,
                is_active=True,
            )
            db.session.add(supplier)
            db.session.commit()
            flash(f"Supplier '{name}' added successfully.", "success")
            return redirect(url_for("masters.suppliers_list"))

        elif action == "edit":
            sup_id = request.form.get("supplier_id")
            supplier = db.session.get(Supplier, int(sup_id))
            if supplier:
                supplier.name = request.form.get("name", "").strip()
                supplier.phone = request.form.get("phone", "").strip()
                supplier.address = request.form.get("address", "").strip()
                supplier.city = request.form.get("city", "").strip()
                db.session.commit()
                flash(f"Supplier '{supplier.name}' updated.", "success")
            return redirect(url_for("masters.suppliers_list"))

    search = request.args.get("search", "").strip()
    query = Supplier.query
    if search:
        query = query.filter(Supplier.name.ilike(f"%{search}%"))
    suppliers = query.order_by(Supplier.name.asc()).all()
    return render_template("masters/suppliers.html", suppliers=suppliers, search=search)


# ================= CUSTOMERS MASTER =================
@masters_bp.route("/customers", methods=["GET", "POST"])
@login_required
def customers_list():
    if request.method == "POST":
        action = request.form.get("action", "add")
        if action == "add":
            name = request.form.get("name", "").strip()
            phone = request.form.get("phone", "").strip()
            address = request.form.get("address", "").strip()
            city = request.form.get("city", "").strip()
            opening_balance = float(request.form.get("opening_balance", 0) or 0)

            if not name:
                flash("Customer Name is required.", "danger")
                return redirect(url_for("masters.customers_list"))

            customer = Customer(
                name=name,
                phone=phone,
                address=address,
                city=city,
                opening_balance=opening_balance,
                current_balance=opening_balance,
                is_active=True,
            )
            db.session.add(customer)
            db.session.commit()
            flash(f"Customer '{name}' added successfully.", "success")
            return redirect(url_for("masters.customers_list"))

        elif action == "edit":
            cust_id = request.form.get("customer_id")
            customer = db.session.get(Customer, int(cust_id))
            if customer:
                customer.name = request.form.get("name", "").strip()
                customer.phone = request.form.get("phone", "").strip()
                customer.address = request.form.get("address", "").strip()
                customer.city = request.form.get("city", "").strip()
                db.session.commit()
                flash(f"Customer '{customer.name}' updated.", "success")
            return redirect(url_for("masters.customers_list"))

    search = request.args.get("search", "").strip()
    query = Customer.query
    if search:
        query = query.filter(Customer.name.ilike(f"%{search}%"))
    customers = query.order_by(Customer.name.asc()).all()
    return render_template("masters/customers.html", customers=customers, search=search)


# ================= PARTNERS REDIRECT =================
@masters_bp.route("/partners-legacy")
@login_required
def partners_list():
    return redirect(url_for("partners.partners_list"))
