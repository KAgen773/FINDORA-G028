from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Fake login data (for now)
USERNAME = "admin"
PASSWORD = "12345"

# 🔹 First page (login page)
@app.route('/')
def login_page():
    return render_template('index.html')

# 🔹 Handle login
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username == USERNAME and password == PASSWORD:
        return redirect(url_for('mainpage'))
    else:
        return "Invalid login. Try again."

# 🔹 Your main menu page
@app.route('/mainpage')
def mainpage():
    return render_template('Mainpage.html')

if __name__ == '__main__':
    app.run(debug=True)