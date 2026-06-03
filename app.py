import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "findora_secret_key"  # Needed later for login sessions

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Create folder if it doesnt exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

users = {}
items = []

# First page (login page)
@app.route("/")
def interface():
    return render_template("interface.html")

# Handle login
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']      #login field is email
    password = request.form['password']

    if username in users and users[username] == password:
        session["user_id"] = username
        return redirect(url_for('mainpage'))
    else:
        return redirect(url_for('interface'))     #stay on login page
       
    

# Register page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # save temporarily
        users[username] = password

        return redirect(url_for("interface"))    #back to login after register

    return render_template("Registerpage.html")


# 🔹 Your main menu page
@app.route('/mainpage')
def mainpage():
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

    items.append(item)

    print(items)

    return redirect(url_for("mainpage"))

if __name__ == '__main__':
    app.run(debug=True)