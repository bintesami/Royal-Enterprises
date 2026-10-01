import os
import sys

# Ensure crockery_app is in the Python search path
crockery_dir = os.path.join(os.path.dirname(__file__), "crockery_app")
if crockery_dir not in sys.path:
    sys.path.insert(0, crockery_dir)

from app import create_app

app = create_app()

if __name__ == "__main__":
    print("=" * 60)
    print(" Crockery Wholesale Partnership Accounting System - Phase 1")
    print(" Server running on http://127.0.0.1:5000")
    print(" Default Login -> Username: admin | Password: admin123")
    print("=" * 60)
    app.run(debug=True, host="127.0.0.1", port=5000)
