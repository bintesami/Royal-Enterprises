from datetime import datetime
from app import db


class Partner(db.Model):
    __tablename__ = "partners"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    cnic = db.Column(db.String(30))
    phone = db.Column(db.String(50))
    address = db.Column(db.String(255))
    profit_share_percentage = db.Column(db.Float, default=50.0)
    capital_balance = db.Column(db.Float, default=0.0)
    current_balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    drawings = db.relationship("PartnerDrawing", backref="partner", lazy=True)

    def __repr__(self):
        return f"<Partner {self.name}>"


class PartnerCapitalTransaction(db.Model):
    __tablename__ = "partner_capital_transactions"

    id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.Integer, db.ForeignKey("partners.id"), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)  # 'Capital Added', 'Capital Returned', 'Opening Capital', 'Profit Share', 'Adjustment'
    amount = db.Column(db.Float, default=0.0, nullable=False)
    description = db.Column(db.String(255))
    reference = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    partner = db.relationship("Partner", backref="capital_transactions")
    account = db.relationship("Account", backref="partner_capital_txs")

    def __repr__(self):
        return f"<PartnerCapitalTransaction Partner:{self.partner_id} Type:{self.transaction_type} Amount:{self.amount}>"
