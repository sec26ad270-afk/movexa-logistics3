from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3, os, secrets
from datetime import date, timedelta

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-before-deployment")
DB = os.path.join(os.path.dirname(__file__), "movexa.db")

SLOTS = ["8:00 AM – 10:00 AM", "10:00 AM – 12:00 PM", "12:00 PM – 2:00 PM",
         "2:00 PM – 4:00 PM", "4:00 PM – 6:00 PM", "6:00 PM – 8:00 PM"]

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS shipments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_id TEXT UNIQUE NOT NULL,
            seller_name TEXT NOT NULL,
            seller_phone TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            customer_phone TEXT NOT NULL,
            address TEXT NOT NULL,
            parcel TEXT NOT NULL,
            delivery_date TEXT,
            delivery_slot TEXT,
            status TEXT NOT NULL DEFAULT 'Order Received',
            partner TEXT DEFAULT 'Not assigned',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

@app.route("/")
def home():
    return render_template("index.html", min_date=date.today().isoformat(),
                           max_date=(date.today()+timedelta(days=30)).isoformat())

@app.route("/book", methods=["POST"])
def book():
    data = {k: request.form.get(k, "").strip() for k in
            ["seller_name","seller_phone","customer_name","customer_phone","address","parcel"]}
    if not all(data.values()):
        flash("Please complete every field.")
        return redirect(url_for("home"))
    tracking = "MVX" + secrets.token_hex(4).upper()
    with db() as con:
        con.execute("""INSERT INTO shipments
            (tracking_id,seller_name,seller_phone,customer_name,customer_phone,address,parcel)
            VALUES (?,?,?,?,?,?,?)""",
            (tracking, data["seller_name"], data["seller_phone"], data["customer_name"],
             data["customer_phone"], data["address"], data["parcel"]))
    return redirect(url_for("track", tracking_id=tracking))

@app.route("/track", methods=["GET","POST"])
def track_lookup():
    if request.method == "POST":
        return redirect(url_for("track", tracking_id=request.form.get("tracking_id","").strip().upper()))
    return render_template("track_lookup.html")

@app.route("/track/<tracking_id>")
def track(tracking_id):
    with db() as con:
        shipment = con.execute("SELECT * FROM shipments WHERE tracking_id=?", (tracking_id.upper(),)).fetchone()
    if not shipment:
        flash("Tracking ID not found.")
        return redirect(url_for("track_lookup"))
    return render_template("track.html", s=shipment, slots=SLOTS,
                           min_date=date.today().isoformat(),
                           max_date=(date.today()+timedelta(days=30)).isoformat())

@app.route("/schedule/<tracking_id>", methods=["POST"])
def schedule(tracking_id):
    delivery_date = request.form.get("delivery_date","")
    slot = request.form.get("delivery_slot","")
    if not delivery_date or slot not in SLOTS or delivery_date < date.today().isoformat():
        flash("Choose a valid future date and available time slot.")
        return redirect(url_for("track", tracking_id=tracking_id))
    with db() as con:
        # Limit each slot to 5 shipments per date in this starter demo.
        count = con.execute("SELECT COUNT(*) FROM shipments WHERE delivery_date=? AND delivery_slot=?",
                            (delivery_date, slot)).fetchone()[0]
        if count >= 5:
            flash("That slot is full. Please choose another time.")
        else:
            con.execute("UPDATE shipments SET delivery_date=?, delivery_slot=?, status='Delivery Scheduled' WHERE tracking_id=?",
                        (delivery_date, slot, tracking_id.upper()))
            flash("Delivery schedule saved!")
    return redirect(url_for("track", tracking_id=tracking_id))

@app.route("/admin")
def admin():
    with db() as con:
        shipments = con.execute("SELECT * FROM shipments ORDER BY created_at DESC").fetchall()
    return render_template("admin.html", shipments=shipments)

@app.route("/partner")
def partner():
    with db() as con:
        shipments = con.execute("SELECT * FROM shipments WHERE status NOT IN ('Delivered','Cancelled') ORDER BY created_at DESC").fetchall()
    return render_template("partner.html", shipments=shipments)

@app.route("/partner/update/<tracking_id>", methods=["POST"])
def partner_update(tracking_id):
    status = request.form.get("status","")
    allowed = ["Picked Up","In Transit","Out for Delivery","Delivered"]
    if status in allowed:
        with db() as con:
            con.execute("UPDATE shipments SET status=? WHERE tracking_id=?", (status, tracking_id.upper()))
        flash("Shipment status updated.")
    return redirect(url_for("partner"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
