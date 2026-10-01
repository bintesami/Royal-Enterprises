from datetime import datetime
from app import db


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100))
    unit = db.Column(db.String(50), default="Pcs")
    cost_price = db.Column(db.Float, default=0.0)
    sale_price = db.Column(db.Float, default=0.0)
    current_stock = db.Column(db.Float, default=0.0)
    min_stock_alert = db.Column(db.Float, default=10.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    purchase_items = db.relationship("PurchaseItem", backref="product", lazy=True)
    sale_items = db.relationship("SaleItem", backref="product", lazy=True)
    stock_movements = db.relationship("StockMovement", backref="product", lazy=True)

    def __repr__(self):
        return f"<Product {self.code} - {self.name}>"
