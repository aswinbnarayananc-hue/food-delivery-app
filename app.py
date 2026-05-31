from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "fooddelivery"

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root1234'
app.config['MYSQL_DB'] = 'food_delivery'

mysql = MySQL(app)

# Home Page
@app.route('/')
def home():
    return redirect('/login')

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        cur = mysql.connection.cursor()

        cur.execute(
            "INSERT INTO users(username,email,password) VALUES(%s,%s,%s)",
            (username, email, password)
        )

        mysql.connection.commit()
        cur.close()

        return redirect('/login')

    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT * FROM users WHERE email=%s",
            [email]
        )

        user = cur.fetchone()

        if user and check_password_hash(user[3], password):

            session['user_id'] = user[0]
            session['username'] = user[1]

            return redirect('/dashboard')

    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():

    if 'user_id' not in session:
        return redirect('/login')

    return render_template(
        'dashboard.html',
        username=session['username']
    )

# Food Menu
@app.route('/menu')
def menu():

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM food_items")

    foods = cur.fetchall()

    return render_template(
        'menu.html',
        foods=foods
    )

# Order Food
@app.route('/order/<int:id>')
def order(id):

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT * FROM food_items WHERE id=%s",
        [id]
    )

    food = cur.fetchone()

    cur.execute(
        """
        INSERT INTO orders
        (user_id,food_name,quantity,total_price,status)
        VALUES(%s,%s,%s,%s,%s)
        """,
        (
            session['user_id'],
            food[1],
            1,
            food[2],
            'Pending'
        )
    )

    mysql.connection.commit()

    return redirect('/menu')

#order history
@app.route('/orders')
def orders():

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT * FROM orders WHERE user_id=%s",
        [session['user_id']]
    )

    orders = cur.fetchall()

    return render_template(
        'orders.html',
        orders=orders
    )
# Logout
@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)