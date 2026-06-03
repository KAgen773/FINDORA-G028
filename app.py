from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Store users
users = {
    "admin": "12345"
}

# 🔹 First page (login page)
@app.route('/')
def login_page():
    return render_template('login.html')

# 🔹 Register page
@app.route('/registerpage')
def register_page():
    return render_template('register.html')

# 🔹 Handle register
@app.route('/register', methods=['POST'])
def register():

    username = request.form['username']
    password = request.form['password']

    # Check if user exists
    if username in users:
        return "Username already exists!"

    # Save new user
    users[username] = password

    return redirect(url_for('login_page'))

# 🔹 Handle login
@app.route('/login', methods=['POST'])
def login():

    username = request.form['username']
    password = request.form['password']

    # Check registered users
    if username in users and users[username] == password:
        return redirect(url_for('mainpage'))
    else:
        return "Invalid login. Try again."

# 🔹 Your main menu page
@app.route('/mainpage')
def mainpage():
    return render_template('Mainpage.html')

if __name__ == '__main__':
    app.run(debug=True)


