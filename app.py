from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Temporary database (in-memory)
users = {}

@app.route("/")
def home():
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users[username] = password

        return redirect(url_for("home"))

    return render_template("register.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    if username in users and users[username] == password:
        return "<h2>Login Successful 🎉</h2><a href='/'>Logout</a>"
    else:
        return "<h2>Invalid Login ❌</h2><a href='/'>Try Again</a>"


if __name__ == "__main__":
    app.run(debug=True)