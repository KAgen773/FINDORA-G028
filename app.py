import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session


app = Flask(__name__)
app.secret_key = "findora_secret_key"  # Needed later for login sessions

db = mysql.connector.connect(
    host="sql12.freesqldatabase.com",
    user="sql12825346",
    password="Sa8Xc2HhZN",
    database="sql12825346"
)

cursor = db.cursor(dictionary=True)


# First page (login page)
@app.route("/")
def interface():
    return render_template("interface.html")

# Handle login
@app.route('/login', methods=['POST'])
def login():
    email = request.form['username']      #login field is email
    password = request.form['password']

    sql = "SELECT * FROM users WHERE email = %s AND password = %s"
    cursor.execute(sql, (email, password))
    user = cursor.fetchone()

    if user:
        session["user_id"] = user["id"]
        return redirect(url_for('mainpage'))
    else:
        return redirect(url_for('interface'))     #stay on login page
       
    

# Register page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        sql = "INSERT INTO users (email,password) VALUES (%s, %s)"
        cursor.execute(sql, (email, password))
        db.commit()

        return redirect(url_for("interface"))    #back to login after register

    return render_template("Registerpage.html")

# 🔹 Your main menu page
@app.route('/mainpage')
def mainpage():
    return render_template('Mainpage.html')

if __name__ == '__main__':
    app.run(debug=True)

@app.route("/report", methods=["POST"])
def report():
    if "user_id" not in session:
        return redirect(url_for("interface"))
    
    item_name = request.form["item_name"]
    location = request.form["location"]
    description = request.form["description"]

    sql = """
    INSERT INTO items (user_id, type, name, description, location)
    VALUES (%s, %s, %s, %s, %s)
    """

    #You need to know if its lost or found
    #simplest fix: add hidden field in HTML (I'll show below)

    item_type = request.form["type"]

    cursor.execute(sql, (
        session["user_id"],
        item_type,
        item_name,
        description,
        location,
    ))

    db.commit()

    return redirect(url_for("mainpage"))

