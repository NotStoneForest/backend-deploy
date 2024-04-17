from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from typing import List
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from datetime import datetime


@login.user_loader
def load_user(id):
    return db.session.get(StaffAdmin, int(id))
class StaffAdmin(UserMixin, db.Model):
    __tablename__ = 'staff_admin'
    id:                 so.Mapped[int] = so.mapped_column(primary_key=True)
    staff_id:           so.Mapped[str] = so.mapped_column(sa.String(64), 
                                            index=True, unique=True)                # Staff can have different prefix letter for different group
    password_hash:      so.Mapped[str] = so.mapped_column(sa.String(256))

    def __init__(self, staff_id, input_password):
        self.staff_id = staff_id
        self.password_hash = generate_password_hash(input_password)

    def __repr__(self):
        return '<|Staff|: staff_id={}, pw_hash={} >'.format(self.staff_id, self.password_hash)

    def set_password(self, input_password):
        self.password_hash = generate_password_hash(input_password)
    def check_password(self, input_password):
        return check_password_hash(self.password_hash, input_password)

class Category(db.Model):
    __tablename__ = 'category'  
    id:                 so.Mapped[int] = so.mapped_column(primary_key=True)
    name:               so.Mapped[str] = so.mapped_column(sa.String(20))
    # description:        so.Mapped[str] = so.mapped_column(sa.String(80), nullable=True)
    rank:               so.Mapped[int] = so.mapped_column(sa.Integer, nullable=True)   

    category_item_map:  so.Mapped[List['MenuItem']] = so.relationship('MenuItem', back_populates='item_category_map')

    def __init__(self, name, rank=0):
        self.name = name
        self.rank = rank

    def __repr__(self):
        return '<|Category|: id={}, name={}, rank={} >'.format(self.id, self.name, self.rank) 

    def to_dict(self):
        return {
            'category_id': self.id,
            'name': self.name,
            'rank': self.rank,
        }

class MenuItem(db.Model):
    __tablename__ = 'menu_item'  
    id:                 so.Mapped[int] = so.mapped_column(primary_key=True)
    name:               so.Mapped[str] = so.mapped_column(sa.String(20))
    price:              so.Mapped[float] = so.mapped_column(sa.Float)
    category_id:        so.Mapped[int] = so.mapped_column(sa.ForeignKey(Category.id))               # foreign key, refers to Category
    description:        so.Mapped[str] = so.mapped_column(sa.String(80), nullable=True)
    ingredients:        so.Mapped[str] = so.mapped_column(sa.String(80), nullable=True)
    image_url:          so.Mapped[str] = so.mapped_column(sa.String(200), nullable=True)
    stock:              so.Mapped[int] = so.mapped_column(sa.Integer)
    status:             so.Mapped[str] = so.mapped_column(sa.String(80))                            # selling / hidden / ...
    rank_incat:         so.Mapped[int] = so.mapped_column(sa.Integer)                               # the order/rank in its category

    item_category_map:       so.Mapped['Category'] = so.relationship('Category', back_populates='category_item_map')

    def __init__(self, name, category_id, price, description, ingredients, image_url, stock, status='selling', rank_incat=0):
        self.name = name
        self.category_id = category_id
        self.price = price
        self.description = description
        self.ingredients = ingredients
        self.image_url = image_url
        self.stock = stock
        self.status= status
        self.rank_incat = rank_incat
    
    def __repr__(self):
        return '<|MenuItem|: id={}, name={}, rank_incat={} >'.format(self.id, self.name, self.rank_incat)

    def to_dict(self):
        return {
            'item_id': self.id,
            'name': self.name,
            'price': self.price,
            'category_id': self.category_id,
            'description': self.description,
            'ingredients': self.ingredients,
            'image_url': self.image_url,
            'stock': self.stock,
            'rank_incat': self.rank_incat,
        }

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.String(50), nullable=False)
    request_type = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default="pending")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, table_number, request_type):
        self.table_number = table_number
        self.request_type = request_type

    def to_dict(self):
        return {
            'request_id': self.id,
            'table_number': self.table_number,
            'request_type': self.request_type,
            'status': self.status,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        }

class Order(db.Model):
    __tablename__ = 'order' 
    id:                 so.Mapped[int] = so.mapped_column(primary_key=True)
    table_number:       so.Mapped[int] = so.mapped_column(sa.Integer)
    status:             so.Mapped[str] = so.mapped_column(sa.String, default='ordering')                # ordering -> checking -> paid
    timestamp:          so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)
    subtotal:           so.Mapped[float] = so.mapped_column(sa.Float)
    order_item_map:     so.Mapped[List['OrderItem']] = so.relationship('OrderItem', back_populates='item_order_map', uselist=True)

    def __init__(self, table_number, subtotal=0):
        self.table_number = table_number
        self.subtotal = subtotal

    def to_dict(self):
        return {
            'order_id': self.id,
            'table_number': self.table_number,
            'status': self.status,
            'timestamp': self.timestamp,
            'subtotal': self.subtotal,
        }

    def to_order(self):
        temp_list = []
        for order_item in self.order_item_map:
            temp_list.append(order_item.to_dict())
        return {
            'order_id': self.id,
            'table_number': self.table_number,
            'ordered_items': temp_list,
            'status': self.status,
            'timestamp': self.timestamp,
            'subtotal': self.subtotal,
        }


class OrderItem(db.Model):
    __tablename__ = 'order_item' 
    id:                 so.Mapped[int] = so.mapped_column(primary_key=True, unique=True)
    order_id:           so.Mapped[int] = so.mapped_column(sa.ForeignKey(Order.id))                  # foreign key, refers to Order
    item_id:            so.Mapped[int] = so.mapped_column(sa.ForeignKey(MenuItem.id))               # foreign key, refers to MenuItem
    item_name:          so.Mapped[str] = so.mapped_column(sa.String(20))
    image_url:          so.Mapped[str] = so.mapped_column(sa.String(200), nullable=True)
    price:              so.Mapped[float] = so.mapped_column(sa.Float)
    quantity:           so.Mapped[int] = so.mapped_column(sa.Integer)

    item_order_map:     so.Mapped['Order'] = so.relationship('Order', back_populates='order_item_map')

    def __init__(self, order_id, item_id, item_name, price, quantity):
        self.order_id = order_id
        self.item_id = item_id
        self.item_name = item_name
        self.price = price
        self.quantity = quantity

    def to_dict(self):
        return {
            'order_item_id': self.id,
            'order_id': self.order_id,
            'item_id': self.item_id,
            'item_name': self.item_name,
            'price': self.price,
            'quantity': self.quantity,
        }

class KitchenOrderItem(db.Model):
    __tablename__ = 'kitchen_order_item' 
    id:                 so.Mapped[int] = so.mapped_column(primary_key=True)
    item_id:            so.Mapped[int] = so.mapped_column(sa.ForeignKey(MenuItem.id))
    image_url:          so.Mapped[str] = so.mapped_column(sa.String(200), nullable=True)
    item_name:          so.Mapped[str] = so.mapped_column(sa.String(20))
    quantity:           so.Mapped[int] = so.mapped_column(sa.Integer)
    table_number:       so.Mapped[int] = so.mapped_column(sa.Integer)
    status:             so.Mapped[str] = so.mapped_column(sa.String, default='cooking')                 # 'cooking' -> 'ready' -> 'delivered'
    timestamp:          so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)

    def __init__(self, item_id, item_name, table_number, quantity, image_url=None):
        self.item_id = item_id
        self.item_name = item_name
        self.image_url = image_url
        self.table_number = table_number
        self.quantity = quantity

    def to_dict(self):
        return {
            'kitchen_order_item_id': self.id,
            'item_id': self.item_id,
            'item_name': self.item_name,
            'image_url': self.image_url,
            'quantity': self.quantity,
            'table_number': self.table_number,
            'status': self.status,
            'timestamp': self.timestamp
        }