from datetime import datetime
from app import db


class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    expense_no = db.Column(db.String(50), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    category = db.Column(db.String(100), nullable=False)  # Expense Head
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(255))
    payee = db.Column(db.String(150), nullable=True)  # Vendor / Paid To
    amount = db.Column(db.Float, default=0.0, nullable=False)
    payment_method = db.Column(db.String(50), default="Cash")
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=True)
    reference = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<Expense {self.title}: {self.amount}>"
