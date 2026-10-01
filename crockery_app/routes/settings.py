import os
import shutil
import json
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app
from flask_login import login_required

settings_bp = Blueprint("settings", __name__)

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "settings.json")
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backups")


def load_settings():
    default_settings = {
        "business_name": "Crockery Wholesale Partnership Accounting System",
        "phone": "+92 300 1234567",
        "address": "Wholesale Crockery Market, Pakistan",
        "currency": "PKR",
        "invoice_footer": "Thank you for doing business with us. Goods once sold will not be returned without bill.",
        "inventory_valuation": "Weighted Average Cost",
    }
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                default_settings.update(data)
        except Exception:
            pass
    return default_settings


def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
        return True
    except Exception:
        return False


@settings_bp.route("/settings", methods=["GET", "POST"])
@login_required
def index():
    settings = load_settings()

    if request.method == "POST":
        action = request.form.get("action", "")
        if action == "save_settings":
            settings["business_name"] = request.form.get("business_name", "").strip() or settings["business_name"]
            settings["phone"] = request.form.get("phone", "").strip()
            settings["address"] = request.form.get("address", "").strip()
            settings["currency"] = request.form.get("currency", "PKR").strip()
            settings["invoice_footer"] = request.form.get("invoice_footer", "").strip()
            settings["inventory_valuation"] = request.form.get("inventory_valuation", "Weighted Average Cost")

            if save_settings(settings):
                flash("System and business settings updated successfully.", "success")
            else:
                flash("Failed to save settings file.", "danger")
            return redirect(url_for("settings.index"))

    # Check existing backups
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR, exist_ok=True)

    backups = []
    for fname in sorted(os.listdir(BACKUP_DIR), reverse=True):
        if fname.endswith(".db"):
            fpath = os.path.join(BACKUP_DIR, fname)
            stat = os.stat(fpath)
            backups.append({
                "filename": fname,
                "size_kb": round(stat.st_size / 1024.0, 1),
                "created_at": datetime.fromtimestamp(stat.st_mtime).strftime("%d-%m-%Y %H:%M:%S"),
            })

    return render_template("settings/index.html", settings=settings, backups=backups)


@settings_bp.route("/settings/backup")
@login_required
def download_backup():
    app_dir = os.path.dirname(os.path.dirname(__file__))
    source_db = os.path.join(app_dir, "database.db")

    if not os.path.exists(source_db):
        flash("Source database not found.", "danger")
        return redirect(url_for("settings.index"))

    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"crockery_backup_{ts}.db"
    dest_path = os.path.join(BACKUP_DIR, backup_filename)

    shutil.copy2(source_db, dest_path)

    return send_file(
        dest_path,
        as_attachment=True,
        download_name=backup_filename,
        mimetype="application/octet-stream",
    )
