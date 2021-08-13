# Mujaid Kariem
# Class 2

# Importing libraries
import hmac
import sqlite3

from flask import Flask, request, jsonify
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS
from flask_mail import Mail, Message
from smtplib import SMTPRecipientsRefused

# Start flask application
app = Flask(__name__)
# Email configuration
CORS(app)
app.config['SECRET_KEY'] = 'super-secret'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'lifeacademy146@gmail.com'
app.config['MAIL_PASSWORD'] = '08062021'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


# Adding data to the user table
def fetch_users():
    with sqlite3.connect('shopping.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            # print(data)
            new_data.append(User(data[0], data[1], data[4]))
    return new_data


users = fetch_users()


# Creating the user table and giving it values
def register_user_table():
    conn = sqlite3.connect('shopping.db')
    print("Database opened successfully.")

    conn.execute("CREATE TABLE IF NOT EXISTS user(id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "first_name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "email TEXT NOT NULL,"
                 "password TEXT NOT NULL)")
    print("User table created successfully.")
    conn.close()


class Cart(object):
    def __init__(self, item_id, product_name, product_type, description, product_quantity, product_price, price_total):
        self.id = item_id
        self.product_name = product_name
        self.product_type = product_type
        self.description = description
        self.product_quantity = product_quantity
        self.product_price = product_price
        self.price_total = price_total


# Adding products to the store table
def fetch_products():
    with sqlite3.connect('shopping.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM store")
        cart = cursor.fetchall()

        new_data = []

        for data in cart:
            new_data.append(Cart(data[1], data[2], data[3], data[4], data[5], data[6]))
    return new_data


# Creating the store table and giving it values
def product_table():
    conn = sqlite3.connect('shopping.db')
    print("Database opened successfully.")

    conn.execute("CREATE TABLE IF NOT EXISTS store(item_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "product_name TEXT NOT NULL,"
                 "product_type TEXT NOT NULL,"
                 "description TEXT NOT NULL,"
                 "product_quantity INTEGER NOT NULL,"
                 "product_price INTEGER NOT NULL,"
                 "price_total INTEGER NOT NULL)")
    print("Store table created successfully.")
    conn.close()


register_user_table()
product_table()

user_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


# To get an access token
def authenticate(first_name, password):
    user = user_table.get(first_name, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    id = payload['identity']
    return userid_table.get(id, None)


jwt = JWT(app, authenticate, identity)


# Route to get an access token
@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


# Route to register users and send an email
@app.route('/user-registration/', methods=["POST"])
def user_registration():
    response = {}

    try:
        if request.method == "POST":

            username = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            password = request.form['password']

            with sqlite3.connect("shopping.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO user("
                                "first_name,"
                                "last_name,"
                                "email,"
                                "password) VALUES(?, ?, ?, ?)", (username, last_name, email, password))
                conn.commit()
                response["Message"] = "User registered successfully."
                response["Status_code"] = 201
                msg = Message('Hello ' + username, sender='lifeacademy146@gmail.com',
                            recipients=[email])
                msg.body = 'Thank you for registering with Checkers.'
                mail.send(msg)
            return response
    except SMTPRecipientsRefused:
        response["Message"] = "Invalid email used."
        response["Status_code"] = 400
        return response


# Route to get an user info
@app.route('/user-info/<int:user_id>', methods=["GET"])
def user_info(user_id):
    response = {}
    with sqlite3.connect("shopping.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE id=" + str(user_id))

        response["Status_code"] = 200
        response["Description"] = "User information retrieved successfully."
        response["data"] = cursor.fetchone()

    return jsonify(response)


# Route to add items to store table
@app.route('/products/', methods=["POST"])
def products():
    response = {}

    try:

        if request.method == "POST":

            product_name = request.form['product_name']
            product_type = request.form['product_type']
            description = request.form['description']
            product_quantity = request.form['product_quantity']
            product_price = request.form['product_price']
            price_total = int(product_price) * int(product_quantity)

            with sqlite3.connect("shopping.db") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO store("
                            "product_name,"
                            "product_type,"
                            "description,"
                            "product_quantity,"
                            "product_price,"
                            "price_total) VALUES(?, ?, ?, ?, ?, ?)",
                            (product_name, product_type, description, product_quantity, product_price, price_total))
                conn.commit()
                response["Message"] = "Product added successfully."
                response["Status_code"] = 201
            return response
    except Exception as e:
        return e


# Route to get an item from store table
@app.route('/get-products/<int:item_id>', methods=["GET"])
def get_products(item_id):
    response = {}
    with sqlite3.connect("shopping.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM store WHERE item_id=" + str(item_id))

        response["Status_code"] = 200
        response["Description"] = "Cart retrieved successfully"
        response["data"] = cursor.fetchone()

    return jsonify(response)


# Route to get all items from store table
@app.route('/show-products/', methods=["GET"])
def show_products():
    response = {}
    with sqlite3.connect("shopping.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM store")

        response["Status_code"] = 200
        response["Description"] = "Cart retrieved successfully"
        response["data"] = cursor.fetchall()

    return jsonify(response)


# Route to update items in store table
@app.route('/update-products/<int:item_id>', methods=["PUT"])
@jwt_required()
def update_products(item_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('shopping.db') as conn:
            incoming_data = dict(request.json)
            put_data = {}
            # To update item quantity
            if incoming_data.get("product_quantity") is not None:
                put_data["product_quantity"] = incoming_data.get("product_quantity")
                with sqlite3.connect('shopping.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE store SET product_quantity =? WHERE item_id=?", (put_data["product_quantity"], item_id))
                    conn.commit()
                    response['Message'] = "Product quantity updated was successful."
                    response['Status_code'] = 200
            # To update item price
            if incoming_data.get("product_price") is not None:
                put_data["product_price"] = incoming_data.get("product_price")
                with sqlite3.connect('shopping.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE store SET product_price =? WHERE item_id=?", (put_data["product_price"], item_id))
                    conn.commit()
                    response['Message'] = "Product price updated was successful."
                    response['Status_code'] = 200
    return response


# Route to remove item from store table
@app.route("/remove-item/<int:item_id>")
def remove_item(item_id):
    response = {}
    with sqlite3.connect("shopping.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM store where item_id=" + str(item_id))
        conn.commit()
        response['Status_code'] = 200
        response['Message'] = "Item removed successfully."
    return response


@app.route('/')
@app.route('/home')
def home():
    return 'Welcome to the home page'


if __name__ == '__main__':
    app.run(debug=True)
