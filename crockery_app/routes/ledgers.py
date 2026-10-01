from flask import Blueprint, render_template, request
from flask_login import login_required
from app import db
from models.supplier import Supplier
from models.purchase import Purchase
from models.customer import Customer
from models.sale import Sale
from models.cash_bank import CashBankTransaction

ledgers_bp = Blueprint("ledgers", __name__)


# ================= SUPPLIER PAYABLE LEDGER =================
@ledgers_bp.route("/supplier-ledger")
@login_required
def supplier_ledger():
    suppliers = Supplier.query.order_by(Supplier.name.asc()).all()
    selected_supplier_id = request.args.get("supplier_id")

    selected_supplier = None
    if selected_supplier_id:
        selected_supplier = db.session.get(Supplier, int(selected_supplier_id))

    # Fetch purchases
    p_query = Purchase.query
    if selected_supplier:
        p_query = p_query.filter_by(supplier_id=selected_supplier.id)
    purchases = p_query.all()

    # Fetch independent payments (vouchers)
    v_query = CashBankTransaction.query.filter_by(transaction_type="Supplier Payment")
    if selected_supplier:
        v_query = v_query.filter_by(reference_id=selected_supplier.id)
    voucher_payments = v_query.all()

    # Build chronological running ledger entries
    ledger_entries = []

    # 1. Opening Balance entry if single supplier
    running_balance = 0.0
    if selected_supplier and selected_supplier.opening_balance > 0:
        running_balance = selected_supplier.opening_balance
        ledger_entries.append({
            "date": selected_supplier.created_at,
            "supplier_name": selected_supplier.name,
            "voucher_no": "OPENING",
            "description": "Opening Payable Balance",
            "debit": 0.0,
            "credit": selected_supplier.opening_balance,
            "balance": running_balance,
        })

    # 2. Add Purchases
    for p in purchases:
        # Credit Purchase (increases payable)
        running_balance += p.total_amount
        ledger_entries.append({
            "date": p.date,
            "supplier_name": p.supplier.name if p.supplier else "N/A",
            "voucher_no": p.bill_no,
            "description": f"Purchase Invoice #{p.bill_no}",
            "debit": 0.0,
            "credit": p.total_amount,
            "balance": running_balance,
        })

        # If paid at bill time, record debit payment (reduces payable)
        if p.paid_amount > 0:
            running_balance -= p.paid_amount
            ledger_entries.append({
                "date": p.date,
                "supplier_name": p.supplier.name if p.supplier else "N/A",
                "voucher_no": f"PAY-{p.bill_no}",
                "description": f"Payment at bill time for #{p.bill_no}",
                "debit": p.paid_amount,
                "credit": 0.0,
                "balance": running_balance,
            })

    # 3. Add subsequent voucher payments
    for v in voucher_payments:
        # Avoid duplicating payment if reference is purchase bill already handled
        if v.reference_type == "Purchase":
            continue
        running_balance -= v.amount
        sup_name = selected_supplier.name if selected_supplier else "Supplier"
        ledger_entries.append({
            "date": v.date,
            "supplier_name": sup_name,
            "voucher_no": f"PV-{v.id:04d}",
            "description": v.description or "Supplier Payment Voucher",
            "debit": v.amount,
            "credit": 0.0,
            "balance": running_balance,
        })

    # Sort chronologically, then calculate strict running balance
    ledger_entries.sort(key=lambda x: x["date"])
    bal = 0.0
    total_debit = 0.0
    total_credit = 0.0
    for entry in ledger_entries:
        bal += (entry["credit"] - entry["debit"])
        entry["balance"] = bal
        total_debit += entry["debit"]
        total_credit += entry["credit"]

    total_outstanding = bal

    # Show newest first for table view
    display_entries = list(reversed(ledger_entries))

    return render_template(
        "ledgers/supplier_ledger.html",
        suppliers=suppliers,
        selected_supplier=selected_supplier,
        ledger_entries=display_entries,
        total_debit=total_debit,
        total_credit=total_credit,
        total_outstanding=total_outstanding,
    )


# ================= CUSTOMER RECEIVABLE LEDGER =================
@ledgers_bp.route("/customer-ledger")
@login_required
def customer_ledger():
    customers = Customer.query.order_by(Customer.name.asc()).all()
    selected_customer_id = request.args.get("customer_id")

    selected_customer = None
    if selected_customer_id:
        selected_customer = db.session.get(Customer, int(selected_customer_id))

    # Fetch Sales
    s_query = Sale.query
    if selected_customer:
        s_query = s_query.filter_by(customer_id=selected_customer.id)
    sales = s_query.all()

    # Fetch independent receipts (vouchers)
    v_query = CashBankTransaction.query.filter_by(transaction_type="Customer Receipt")
    if selected_customer:
        v_query = v_query.filter_by(reference_id=selected_customer.id)
    voucher_receipts = v_query.all()

    # Build chronological running ledger entries
    ledger_entries = []

    # 1. Opening Balance entry
    if selected_customer and selected_customer.opening_balance > 0:
        ledger_entries.append({
            "date": selected_customer.created_at,
            "customer_name": selected_customer.name,
            "voucher_no": "OPENING",
            "description": "Opening Receivable Balance",
            "debit": selected_customer.opening_balance,
            "credit": 0.0,
            "balance": selected_customer.opening_balance,
        })

    # 2. Add Sales
    for s in sales:
        ledger_entries.append({
            "date": s.date,
            "customer_name": s.customer.name if s.customer else "N/A",
            "voucher_no": s.invoice_no,
            "description": f"Sales Invoice #{s.invoice_no}",
            "debit": s.total_sale,
            "credit": 0.0,
            "balance": 0.0,
        })

        if s.received_amount > 0:
            ledger_entries.append({
                "date": s.date,
                "customer_name": s.customer.name if s.customer else "N/A",
                "voucher_no": f"REC-{s.invoice_no}",
                "description": f"Receipt at delivery for #{s.invoice_no}",
                "debit": 0.0,
                "credit": s.received_amount,
                "balance": 0.0,
            })

    # 3. Add subsequent voucher receipts
    for v in voucher_receipts:
        if v.reference_type == "Sale":
            continue
        cust_name = selected_customer.name if selected_customer else "Customer"
        ledger_entries.append({
            "date": v.date,
            "customer_name": cust_name,
            "voucher_no": f"RV-{v.id:04d}",
            "description": v.description or "Customer Payment Receipt Voucher",
            "debit": 0.0,
            "credit": v.amount,
            "balance": 0.0,
        })

    # Sort chronologically, then calculate running balance:
    # Customer Ledger: Debit increases receivable, Credit reduces receivable
    ledger_entries.sort(key=lambda x: x["date"])
    bal = 0.0
    total_debit = 0.0
    total_credit = 0.0
    for entry in ledger_entries:
        bal += (entry["debit"] - entry["credit"])
        entry["balance"] = bal
        total_debit += entry["debit"]
        total_credit += entry["credit"]

    total_outstanding = bal
    display_entries = list(reversed(ledger_entries))

    return render_template(
        "ledgers/customer_ledger.html",
        customers=customers,
        selected_customer=selected_customer,
        ledger_entries=display_entries,
        total_debit=total_debit,
        total_credit=total_credit,
        total_outstanding=total_outstanding,
    )
