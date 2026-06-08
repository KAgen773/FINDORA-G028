import os
import math
import re
from collections import Counter
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "findora_secret_key"  # Needed later for login sessions

WEIGHT_TYPE = 50
WEIGHT_LOCATION_EXACT = 30
WEIGHT_LOCATION_NEAR = 15
WEIGHT_DATE_PROXIMITY = 10
WEIGHT_DESC = 20

def get_db():
    conn = psycopg2.connect(
        host="aws-1-ap-northeast-2.pooler.supabase.com",
        database="postgres",
        user="postgres.nlcxhkwuhntanpvigjpo",
        password="Kavin7374@!",
        port="5432",
        cursor_factory=RealDictCursor
    )
    return conn

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Create folder if it doesnt exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

users = {}

def preprocess_text(text):
    if not text:
        return []
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return [word for word in text.split() if word]

def description_similarity(desc_a, desc_b):
    tokens_a = preprocess_text(desc_a)
    tokens_b = preprocess_text(desc_b)

    if not tokens_a or not tokens_b:
        return 0.0
    
    counts_a = Counter(tokens_a)
    counts_b = Counter(tokens_b)

    vocab = set(counts_a.keys()).union(set(counts_b.keys()))

    dot_product = sum(counts_a.get(word, 0) * counts_b.get(word, 0) for word in vocab)
    norm_a = math.sqrt(sum(count ** 2 for count in counts_a.values()))
    norm_b = math.sqrt(sum(count ** 2 for count in counts_b.values()))

    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)

def calculate_match_score(item_a, item_b):

    score = 0

    type_a = str(item_a.get('type', '')).strip().lower()
    type_b = str(item_b.get('type', '')).strip().lower()
    
    if type_a == type_b:
        return 0.0
    score += WEIGHT_TYPE

    loc_a = str(item_a.get('location', '')).strip().lower()
    loc_b = str(item_b.get('location', '')).strip().lower()

    if loc_a == loc_b:
        score += WEIGHT_LOCATION_EXACT
    elif loc_a in loc_b or loc_b in loc_a:
        score += WEIGHT_LOCATION_NEAR

    try:
        date_a = item_a.get('date')
        date_b = item_b.get('date')
        if date_a and date_b:
            days_diff = abs((date_a - date_b).days)
            if days_diff <= 3:
                score += WEIGHT_DATE_PROXIMITY
    except Exception:
        pass

    combined_a = f"{item_a.get('name', '')} {item_a.get('description', '')}"
    combined_b = f"{item_b.get('name', '')} {item_b.get('description', '')}"

    sim_ratio = description_similarity(combined_a, combined_b)
    score += sim_ratio * WEIGHT_DESC

    return round(score, 2)


# First page (login page)
@app.route("/")
def interface():
    return render_template("interface.html")


# Handle login
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']      #login field is email
    password = request.form['password']

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, username FROM users
        WHERE email=%s AND password=%s
    """, (email, password))

    user = cursor.fetchone()
    conn.close()

    if user:
        session["user_id"] = user['id']
        return redirect(url_for("mainpage"))
    else:
        return redirect(url_for("interface"))   #stay on login page
       
    

# Register page
@app.route("/register", methods=["GET", "POST"])
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

        return redirect(url_for("interface"))    #back to login after register

    return render_template("Registerpage.html")


# 🔹 Your main menu page
@app.route('/mainpage')
def mainpage():
    if "user_id" not in session:
        return redirect(url_for("interface"))  #security check
    
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM items")
    all_items = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) AS total_count FROM items")
    total_result = cursor.fetchone()
    total_reports = total_result['total_count'] if total_result else 0

    cursor.execute("SELECT COUNT(*) AS user_count FROM items WHERE user_id = %s", (str(session["user_id"]),))
    user_result = cursor.fetchone()
    user_reports = user_result['user_count'] if user_result else 0

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

    return render_template('Mainpage.html', items=processed_items, user_reports=user_reports, total_reports=total_reports)


# Report route
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

    # handle image
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

if __name__ == '__main__':
    app.run(debug=True)