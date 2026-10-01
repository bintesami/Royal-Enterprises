import os

basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key")
DATABASE_NAME = "database.db"
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL", f"sqlite:///{os.path.join(basedir, DATABASE_NAME)}"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False

CURRENCY = "PKR"
BUSINESS_NAME = "Crockery Wholesale Partnership Accounting System"
