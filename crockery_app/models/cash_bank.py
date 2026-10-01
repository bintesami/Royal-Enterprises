from datetime import datetime
from app import db


class Account(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.String(50), default="Cash")  # 'Cash' or 'Bank'
    account_number = db.Column(db.String(100))
    bank_name = db.Column(db.String(100))
    balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    transactions = db.relationship(
        "CashBankTransaction", backref="account", lazy=True
    )
    expenses = db.relationship("Expense", backref="account", lazy=True)
    drawings = db.relationship("PartnerDrawing", backref="account", lazy=True)
    journal_lines = db.relationship("JournalLine", backref="account", lazy=True)

    def __repr__(self):
        return f"<Account {self.account_name} ({self.account_type})>"


class CashBankTransaction(db.Model):
    __tablename__ = "cash_bank_transactions"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=False)
    amount = db.Column(db.Float, default=0.0, nullable=False)
    reference_type = db.Column(db.String(50))
    reference_id = db.Column(db.Integer)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<CashBankTransaction {self.transaction_type}: {self.amount}>"


class PartnerDrawing(db.Model):
    __tablename__ = "partner_drawings"

    id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.Integer, db.ForeignKey("partners.id"), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    amount = db.Column(db.Float, default=0.0, nullable=False)
    payment_method = db.Column(db.String(50), default="Cash")
    description = db.Column(db.String(255))
    approved_by = db.Column(db.String(100), nullable=True)
    remarks = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<PartnerDrawing Partner:{self.partner_id} Amount:{self.amount}>"


class JournalEntry(db.Model):
    __tablename__ = "journal_entries"

    id = db.Column(db.Integer, primary_key=True)
    entry_number = db.Column(db.String(50), unique=True, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    reference = db.Column(db.String(100))
    description = db.Column(db.String(255))
    is_posted = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    lines = db.relationship(
        "JournalLine",
        backref="journal_entry",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def __repr__(self):
        return f"<JournalEntry {self.entry_number}>"


class JournalLine(db.Model):
    __tablename__ = "journal_lines"

    id = db.Column(db.Integer, primary_key=True)
    journal_entry_id = db.Column(
        db.Integer, db.ForeignKey("journal_entries.id"), nullable=False
    )
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"), nullable=False)
    debit = db.Column(db.Float, default=0.0)
    credit = db.Column(db.Float, default=0.0)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<JournalLine Entry:{self.journal_entry_id} Dr:{self.debit} Cr:{self.credit}>"
