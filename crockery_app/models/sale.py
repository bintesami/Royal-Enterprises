from datetime import datetime
from app import db


class Sale(db.Model):
    __tablename__ = "sales"

    id = db.Column(db.Integer, primary_key=True)
    invoice_no = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    total_cost = db.Column(db.Float, default=0.0)
    total_sale = db.Column(db.Float, default=0.0)
    gross_profit = db.Column(db.Float, default=0.0)
    received_amount = db.Column(db.Float, default=0.0)
    balance_amount = db.Column(db.Float, default=0.0)
    payment_status = db.Column(db.String(50), default="Pending")
    notes = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    items = db.relationship(
        "SaleItem", backref="sale", cascade="all, delete-orphan", lazy=True
    )

    def __repr__(self):
        return f"<Sale {self.invoice_no}>"


class SaleItem(db.Model):
    __tablename__ = "sale_items"

    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey("sales.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Float, default=0.0)
    unit = db.Column(db.String(50))
    cost_rate = db.Column(db.Float, default=0.0)
    sale_rate = db.Column(db.Float, default=0.0)
    cost_total = db.Column(db.Float, default=0.0)
    sale_total = db.Column(db.Float, default=0.0)
    profit = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<SaleItem Sale:{self.sale_id} Product:{self.product_id}>"
