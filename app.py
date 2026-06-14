import os
import math
import re
from collections import Counter
from flask import Flask, render_template, request, redirect, url_for

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    psycopg2 = None
    RealDictCursor = None

from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)

# Fake login data (for now)
USERNAME = "admin"
PASSWORD = "12345"

# 🔹 First page (login page)
@app.route('/')
def login_page():
    return render_template('login.html')

# 🔹 Handle login
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username == USERNAME and password == PASSWORD:
        return redirect(url_for('login.html'))
    else:
        # Redirects back to the login page if details are wrong
        return redirect(url_for("login_page"))

# -------------------------
# REGISTER
# -------------------------
# -------------------------
# REGISTER
# -------------------------
@app.route("/registerpage", methods=["GET", "POST"])  # ← Add @ here!
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users (username, email, password)
            VALUES (%s, %s, %s)
        """, (username, email, password))

        conn.commit()
        conn.close()

        return redirect(url_for("interface"))
    
    return render_template("registerpage.html")
# -------------------------
# MAIN PAGE
# -------------------------
@app.route('/mainpage')
def mainpage():
    if "user_id" not in session:
        return redirect(url_for("interface"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM items")
    all_items = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) AS active_count FROM items")
    active_reports = cursor.fetchone()['active_count']

    cursor.execute("SELECT COUNT(*) AS found_count FROM items WHERE type='found'")
    found_items = cursor.fetchone()['found_count']

    conn.close()

    processed_items = []

    for current_item in all_items:
        best_match_score = 0

        for comparing_item in all_items:
            if current_item['id'] != comparing_item['id']:
                score = calculate_match_score(current_item, comparing_item)
                if score > best_match_score:
                    best_match_score = score

        item_data = dict(current_item)
        item_data['match_score'] = best_match_score
        processed_items.append(item_data)

    return render_template(
        'Mainpage.html',
        items=processed_items,
        active_reports=active_reports,
        found_items=found_items
    )


# -------------------------
# REPORT ITEM
# -------------------------
@app.route("/report", methods=["POST"])
def report():
    if "user_id" not in session:
        return redirect(url_for("interface"))

    item_name = request.form["item_name"]
    location = request.form["location"]
    date = request.form["date"]
    description = request.form["description"]
    item_type = request.form["type"]
    phone = request.form["phone"]

    image = request.files["image"]
    filename = secure_filename(image.filename)
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    image.save(image_path)

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO items (user_id, type, name, location, date, description, phone, image_url)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        session["user_id"],
        item_type,
        item_name,
        location,
        date,
        description,
        phone,
        image_path
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("mainpage"))


# -------------------------
# RUN APP
# -------------------------
if __name__ == '__main__':
    app.run(debug=True)


