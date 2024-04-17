from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_httpauth import HTTPBasicAuth
from datetime import datetime
from app import db

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///restaurant.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)
# auth = HTTPBasicAuth()

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Table Model
class Table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seats = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='available')  # 'available', 'reserved'

# Dish Model
class Dish(db.Model):   #food list
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Float, nullable=False)

# Order Model    #order
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_id = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False, default=0.0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True)

# OrderItem Model
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    dish_id = db.Column(db.Integer, db.ForeignKey('dish.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    dish = db.relationship('Dish')

@app.before_first_request
def create_tables():
    db.create_all()

@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists.'}), 400
    user = User(username=data['username'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully.'}), 201

@app.route('/login', methods=['GET'])
@auth.login_required
def login():
    return jsonify({'message': 'Hello, {}! You are logged in.'.format(auth.current_user().username)})

# Table Routes
@app.route('/tables', methods=['GET'])
def get_tables():
    tables = Table.query.all()
    return jsonify([{'id': table.id, 'seats': table.seats, 'status': table.status} for table in tables])

@app.route('/reserve', methods=['POST'])
@auth.login_required
def reserve_table():
    table_id = request.json.get('table_id')
    table = Table.query.get(table_id)
    if table and table.status == 'available':
        table.status = 'reserved'
        db.session.commit()
        return jsonify({'message': 'Table reserved successfully.'}), 200
    else:
        return jsonify({'message': 'Table is not available.'}), 400

# Menu Routes
@app.route('/menu', methods=['GET'])
def get_menu():
    dishes = Dish.query.all()
    return jsonify([{'id': dish.id, 'name': dish.name, 'description': dish.description, 'price': dish.price} for dish in dishes])

# Order Routes
@app.route('/order', methods=['POST'])
@auth.login_required
def create_order():
    data = request.json
    new_order = Order(table_id=data['table_id'])
    db.session.add(new_order)
    db.session.commit()
    
    total_price = 0
    for item in data['items']:
        order_item = OrderItem(order_id=new_order.id, dish_id=item['dish_id'], quantity=item['quantity'])
        db.session.add(order_item)
        dish = Dish.query.get(item['dish_id'])
        total_price += dish.price * item['quantity']
    
    new_order.total_price = total_price
    db.session.commit()
    return jsonify({'message': 'Order created successfully.', 'order_id': new_order.id, 'total_price': total_price}), 200

# Dummy Payment Route
@app.route('/pay', methods=['POST'])
@auth.login_required
def pay_order():
    order_id = request.json.get('order_id')
    # Process payment...
    return jsonify({'message': 'Payment processed successfully.'}), 200

# if __name__ == '__main__':
#     app.run(debug=True)
