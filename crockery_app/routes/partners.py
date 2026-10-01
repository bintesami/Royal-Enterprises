from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy import func
from app import db
from models.partner import Partner, PartnerCapitalTransaction
from models.cash_bank import Account, CashBankTransaction, PartnerDrawing

partners_bp = Blueprint("partners", __name__)


@partners_bp.route("/partners", methods=["GET", "POST"])
@login_required
def partners_list():
    if request.method == "POST":
        action = request.form.get("action", "")
        if action == "update_partner":
            partner_id = request.form.get("partner_id")
            partner = db.session.get(Partner, int(partner_id))
            if partner:
                partner.name = request.form.get("name", "").strip()
                partner.phone = request.form.get("phone", "").strip()
                partner.cnic = request.form.get("cnic", "").strip()
                partner.address = request.form.get("address", "").strip()
                partner.profit_share_percentage = float(
                    request.form.get("profit_share", 50.0) or 50.0
                )
                db.session.commit()
                flash(f"Partner '{partner.name}' details updated.", "success")
            return redirect(url_for("partners.partners_list"))

    partners = Partner.query.order_by(Partner.id.asc()).all()

    # Metrics
    total_capital = sum(p.capital_balance or 0.0 for p in partners)
    total_current_balance = sum(p.current_balance or 0.0 for p in partners)
    total_drawings = (
        db.session.query(func.coalesce(func.sum(PartnerDrawing.amount), 0.0)).scalar()
        or 0.0
    )

    # Recent Capital Transactions
    recent_capital_txs = (
        PartnerCapitalTransaction.query.order_by(
            PartnerCapitalTransaction.date.desc(), PartnerCapitalTransaction.id.desc()
        )
        .limit(20)
        .all()
    )

    return render_template(
        "partners/index.html",
        partners=partners,
        total_capital=total_capital,
        total_current_balance=total_current_balance,
        total_drawings=total_drawings,
        recent_capital_txs=recent_capital_txs,
    )


@partners_bp.route("/partners/capital/new", methods=["GET", "POST"])
@login_required
def capital_new():
    partners = Partner.query.order_by(Partner.name.asc()).all()
    accounts = Account.query.order_by(Account.account_name.asc()).all()

    if request.method == "POST":
        partner_id = request.form.get("partner_id")
        date_str = request.form.get("date", "").strip()
        tx_type = request.form.get("transaction_type", "Capital Added")
        amount_raw = request.form.get("amount", "0").strip()
        account_id_raw = request.form.get("account_id", "").strip()
        description = request.form.get("description", "").strip()
        reference = request.form.get("reference", "").strip()

        try:
            amount = float(amount_raw)
        except ValueError:
            amount = 0.0

        if not partner_id:
            flash("Please select a partner.", "danger")
            return redirect(url_for("partners.capital_new"))

        partner = db.session.get(Partner, int(partner_id))
        if not partner:
            flash("Partner not found.", "danger")
            return redirect(url_for("partners.capital_new"))

        if amount <= 0:
            flash("Amount must be greater than zero.", "danger")
            return redirect(url_for("partners.capital_new"))

        try:
            tx_date = (
                datetime.strptime(date_str, "%Y-%m-%d")
                if date_str
                else datetime.utcnow()
            )
        except ValueError:
            tx_date = datetime.utcnow()

        account = None
        if account_id_raw:
            try:
                account = db.session.get(Account, int(account_id_raw))
            except (ValueError, TypeError):
                pass

        # Create Capital Transaction
        cap_tx = PartnerCapitalTransaction(
            partner_id=partner.id,
            account_id=account.id if account else None,
            date=tx_date,
            transaction_type=tx_type,
            amount=amount,
            description=description,
            reference=reference,
        )
        db.session.add(cap_tx)
        db.session.flush()

        # Update partner balances
        if tx_type in ("Capital Added", "Opening Capital"):
            partner.capital_balance = (partner.capital_balance or 0.0) + amount
            partner.current_balance = (partner.current_balance or 0.0) + amount

            # If deposited into business cash/bank account
            if account:
                account.balance = (account.balance or 0.0) + amount
                cb_tx = CashBankTransaction(
                    account_id=account.id,
                    date=tx_date,
                    transaction_type="Partner Capital",
                    amount=amount,
                    reference_type="PartnerCapital",
                    reference_id=cap_tx.id,
                    description=f"Capital contribution from {partner.name}: {description or 'Capital added'}",
                )
                db.session.add(cb_tx)

        elif tx_type in ("Capital Returned", "Capital Withdrawal"):
            partner.capital_balance = (partner.capital_balance or 0.0) - amount
            partner.current_balance = (partner.current_balance or 0.0) - amount

            # If paid out from business cash/bank account
            if account:
                account.balance = (account.balance or 0.0) - amount
                cb_tx = CashBankTransaction(
                    account_id=account.id,
                    date=tx_date,
                    transaction_type="Capital Returned",
                    amount=amount,
                    reference_type="PartnerCapital",
                    reference_id=cap_tx.id,
                    description=f"Capital returned to {partner.name}: {description or 'Capital withdrawal'}",
                )
                db.session.add(cb_tx)

        db.session.commit()
        flash(
            f"{tx_type} of PKR {amount:,.2f} recorded for {partner.name} successfully.",
            "success",
        )
        return redirect(url_for("partners.partners_list"))

    return render_template(
        "partners/capital_new.html",
        partners=partners,
        accounts=accounts,
        today=datetime.utcnow().strftime("%Y-%m-%d"),
    )


@partners_bp.route("/partner-drawings")
@login_required
def drawings_list():
    partner_id = request.args.get("partner_id", "").strip()
    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()

    query = PartnerDrawing.query

    if partner_id:
        try:
            query = query.filter_by(partner_id=int(partner_id))
        except ValueError:
            pass

    if start_date:
        try:
            s_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(PartnerDrawing.date >= s_dt)
        except ValueError:
            pass

    if end_date:
        try:
            e_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(
                hour=23, minute=59, second=59
            )
            query = query.filter(PartnerDrawing.date <= e_dt)
        except ValueError:
            pass

    drawings = query.order_by(
        PartnerDrawing.date.desc(), PartnerDrawing.id.desc()
    ).all()
    partners = Partner.query.order_by(Partner.name.asc()).all()

    total_drawings = sum(d.amount or 0.0 for d in drawings)

    return render_template(
        "partners/drawings_index.html",
        drawings=drawings,
        partners=partners,
        partner_id=partner_id,
        start_date=start_date,
        end_date=end_date,
        total_drawings=total_drawings,
    )


@partners_bp.route("/partner-drawings/new", methods=["GET", "POST"])
@login_required
def drawing_new():
    partners = Partner.query.order_by(Partner.name.asc()).all()
    accounts = Account.query.order_by(Account.account_name.asc()).all()

    if request.method == "POST":
        partner_id = request.form.get("partner_id")
        date_str = request.form.get("date", "").strip()
        account_id_raw = request.form.get("account_id", "").strip()
        amount_raw = request.form.get("amount", "0").strip()
        description = request.form.get("description", "").strip()
        approved_by = request.form.get("approved_by", "").strip()
        remarks = request.form.get("remarks", "").strip()

        try:
            amount = float(amount_raw)
        except ValueError:
            amount = 0.0

        if not partner_id:
            flash("Please select a partner.", "danger")
            return redirect(url_for("partners.drawing_new"))

        partner = db.session.get(Partner, int(partner_id))
        if not partner:
            flash("Partner not found.", "danger")
            return redirect(url_for("partners.drawing_new"))

        if not account_id_raw:
            flash("Please select a Cash or Bank account for withdrawal.", "danger")
            return redirect(url_for("partners.drawing_new"))

        account = db.session.get(Account, int(account_id_raw))
        if not account:
            flash("Account not found.", "danger")
            return redirect(url_for("partners.drawing_new"))

        if amount <= 0:
            flash("Drawing amount must be greater than zero.", "danger")
            return redirect(url_for("partners.drawing_new"))

        try:
            drawing_date = (
                datetime.strptime(date_str, "%Y-%m-%d")
                if date_str
                else datetime.utcnow()
            )
        except ValueError:
            drawing_date = datetime.utcnow()

        # Create PartnerDrawing
        drawing = PartnerDrawing(
            partner_id=partner.id,
            account_id=account.id,
            date=drawing_date,
            amount=amount,
            payment_method=account.account_type,
            description=description,
            approved_by=approved_by,
            remarks=remarks,
        )
        db.session.add(drawing)
        db.session.flush()

        # Deduct from Cash/Bank Account
        account.balance = (account.balance or 0.0) - amount
        cb_tx = CashBankTransaction(
            account_id=account.id,
            date=drawing_date,
            transaction_type="Partner Drawing",
            amount=amount,
            reference_type="PartnerDrawing",
            reference_id=drawing.id,
            description=f"Partner Drawing: {partner.name} - {description or 'Personal withdrawal'}",
        )
        db.session.add(cb_tx)

        # Deduct from Partner's Current Balance
        partner.current_balance = (partner.current_balance or 0.0) - amount

        db.session.commit()
        flash(
            f"Drawing voucher for PKR {amount:,.2f} recorded for {partner.name}.",
            "success",
        )
        return redirect(url_for("partners.drawings_list"))

    return render_template(
        "partners/drawing_new.html",
        partners=partners,
        accounts=accounts,
        today=datetime.utcnow().strftime("%Y-%m-%d"),
    )


@partners_bp.route("/partners/<int:id>/statement")
@login_required
def partner_statement(id):
    partner = db.session.get(Partner, id)
    if not partner:
        flash("Partner not found.", "danger")
        return redirect(url_for("partners.partners_list"))

    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()

    # Collect Capital Transactions
    cap_query = PartnerCapitalTransaction.query.filter_by(partner_id=partner.id)
    # Collect Drawings
    draw_query = PartnerDrawing.query.filter_by(partner_id=partner.id)

    if start_date:
        try:
            s_dt = datetime.strptime(start_date, "%Y-%m-%d")
            cap_query = cap_query.filter(PartnerCapitalTransaction.date >= s_dt)
            draw_query = draw_query.filter(PartnerDrawing.date >= s_dt)
        except ValueError:
            pass

    if end_date:
        try:
            e_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(
                hour=23, minute=59, second=59
            )
            cap_query = cap_query.filter(PartnerCapitalTransaction.date <= e_dt)
            draw_query = draw_query.filter(PartnerDrawing.date <= e_dt)
        except ValueError:
            pass

    cap_txs = cap_query.all()
    drawings = draw_query.all()

    # Merge into double-entry ledger stream
    # Credit increases partner balance (Capital Added, Profit Share)
    # Debit decreases partner balance (Capital Returned, Drawings)
    entries = []

    for c in cap_txs:
        if c.transaction_type in ("Capital Added", "Opening Capital", "Profit Share"):
            entries.append({
                "date": c.date,
                "type": c.transaction_type,
                "description": c.description or "Capital Added",
                "reference": c.reference or f"CAP-{c.id}",
                "debit": 0.0,
                "credit": c.amount,
            })
        else:
            entries.append({
                "date": c.date,
                "type": c.transaction_type,
                "description": c.description or "Capital Returned",
                "reference": c.reference or f"CAP-{c.id}",
                "debit": c.amount,
                "credit": 0.0,
            })

    for d in drawings:
        entries.append({
            "date": d.date,
            "type": "Partner Drawing",
            "description": d.description or "Personal Drawing / Withdrawal",
            "reference": f"DRW-{d.id}",
            "debit": d.amount,
            "credit": 0.0,
        })

    # Sort chronologically
    entries.sort(key=lambda x: x["date"])

    # Calculate running balance
    running_balance = 0.0
    for e in entries:
        running_balance += e["credit"] - e["debit"]
        e["balance"] = running_balance

    total_debit = sum(e["debit"] for e in entries)
    total_credit = sum(e["credit"] for e in entries)

    all_partners = Partner.query.order_by(Partner.name.asc()).all()

    return render_template(
        "partners/statement.html",
        partner=partner,
        all_partners=all_partners,
        entries=entries,
        total_debit=total_debit,
        total_credit=total_credit,
        final_balance=running_balance,
        start_date=start_date,
        end_date=end_date,
    )
