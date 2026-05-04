from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Temporary database (in-memory)
users = {}

# First page (login page)
@app.route("/")
def interface():
    return render_template("interface.html")

# Handle login
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']


    if username in users and users[username] == password:
        return redirect(url_for('mainpage'))
    else:
        return redirect(url_for('interface'))     #stay on login page
    

# Register page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users[username] = password

        return redirect(url_for("interface"))    #back to login after register

    return render_template("Registerpage.html")

# 🔹 Your main menu page
@app.route('/mainpage')
def mainpage():
    return render_template('Mainpage.html')

if __name__ == '__main__':
    app.run(debug=True)