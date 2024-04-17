import sqlalchemy as sa
import sqlalchemy.orm as so
from app import app, db
from app.models import StaffAdmin, MenuItem, Category, Request, Order, OrderItem

@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'StaffAdmin': StaffAdmin,
            'MenuItem': MenuItem, 'Category': Category, 'Request': Request,
            'Order': Order, 'OrderItem': OrderItem
    }