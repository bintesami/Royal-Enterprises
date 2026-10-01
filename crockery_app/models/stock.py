from datetime import datetime
from app import db


class StockMovement(db.Model):
    __tablename__ = "stock_movements"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    movement_type = db.Column(
        db.String(50), nullable=False
    )  # 'IN', 'OUT', 'ADJUSTMENT'
    quantity = db.Column(db.Float, default=0.0, nullable=False)
    unit_cost = db.Column(db.Float, default=0.0)
    reference_type = db.Column(
        db.String(50)
    )  # 'Purchase', 'Sale', 'Opening', 'Adjustment'
    reference_id = db.Column(db.Integer)
    notes = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<StockMovement Product:{self.product_id} Type:{self.movement_type} Qty:{self.quantity}>"
