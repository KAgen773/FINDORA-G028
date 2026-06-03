import os
import psycopg2
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "findora_secret_key"  # Needed later for login sessions

from psycopg2.extras import RealDictCursor

def get_db():
    conn = psycopg2.connect(
        host="aws-1-ap-northeast-2.pooler.supabase.com",
        database="postgres",
        user="postgres.nlcxhkwuhntanpvigjpo",
        password="Kavinnesh73@",
        port="5432",
        cursor_factory=RealDictCursor
    )
    return conn


UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Create folder if it doesnt exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

users = {}


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
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()

    conn.close()

    return render_template('Mainpage.html', items=items)


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

    item = {
        "user": session["user_id"],
        "type": item_type,
        "name": item_name,
        "location": location,
        "date": date,
        "description": description,
        "phone": phone,
        "image": image_path
    }

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