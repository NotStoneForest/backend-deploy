import os
from app import app
from app import db
from flask import jsonify, request, send_from_directory
from sqlalchemy.orm import sessionmaker
import sqlalchemy as sa
from app.models import StaffAdmin, MenuItem, Category, Request, Order, OrderItem, KitchenOrderItem
from flask_login import current_user, login_user, login_required
from werkzeug.utils import secure_filename
import uuid
from .utils.utils import response_template

IMAGE_PATH_PREFIX = '/static/images/'

# =================================  Tests  ====================================
@app.route('/')
def index():
    return "Welcome to index page"
@app.route('/hello')
def hello():
    return "hello from backend :)"

# =================================  Login  ====================================
@app.route('/api/s/login', methods=['POST'])
def staff_login():
    data = request.get_json()
    staff_id = data.get('staff_id')
    password = data.get('password')
    staff = StaffAdmin.query.filter_by(staff_id = staff_id).first()
    if (staff is None) or (not staff.check_password(password)):
        return response_template(False, 500, 'Fail: staff_login()', None)

    return response_template(True, 200, 'Success: staff_login()', None)

@app.route('/api/s/change_password', methods=['POST'])
def change_password():
    data = request.get_json()
    staff_id = data['staff_id']
    new_pw = data['password']
    staff = StaffAdmin.query.filter_by(staff_id = staff_id).first()
    if (not staff):
        return response_template(False, 500, 'Not found staff with id: {}'.format(staff_id), None)
    staff.set_password(new_pw)
    try:
        db.session.commit()
        return response_template(True, 200, 'Success: change_password()', None)
    except Exception as e:
        db.session.rollback()
        return response_template(False, 500, 'Fail: change_password()', {'error': str(e)})

# =================================  Images  ===================================
@app.route('/static/images/<image_name>', methods=['GET'])
def serve_image(image_name):
    response = send_from_directory(app.config['IMAGE_FOLDER'], image_name)
    response.cache_control.max_age = 604800
    return response

# ==============================================================================
# =================================  Category  =================================
# ==============================================================================
@app.route('/api/s/menu/category/new', methods=['POST'])
def create_new_category():
    data = request.get_json()
    cat_name = data.get('name')
    new_cat = Category(cat_name)
    db.session.add(new_cat)

    try:
        db.session.commit()
        cat_list = Category.query.order_by('rank').all()
        cat_list = [cat.to_dict() for cat in cat_list]
        return response_template(True, 200, 'New category created successfully', cat_list)
    except Exception as e:
        db.session.rollback()
        return response_template(False, 500, 'Failed to create new category', {'error': str(e)})
    
@app.route('/api/s/menu/category/rank', methods=['POST'])
def order_category():
    cat_rank_list = request.get_json()
    for cat_rank in cat_rank_list:
        category = Category.query.get(cat_rank['category_id'])
        if (category):
            category.rank = cat_rank['rank']
        else:
            return response_template(False, 500, 'Failed to get category: {}'.format(cat_rank['category_id']), None)

    try:
        db.session.commit()
        cat_list = Category.query.order_by('rank').all()
        cat_list = [cat.to_dict() for cat in cat_list]
        return response_template(True, 200, 'Categories ordered successfully', cat_list)
    except Exception as e:
        db.session.rollback()
        return response_template(False, 500, 'Failed to order categories', {'error': str(e)})

# ==============================================================================
# =================================  Menu  =====================================
# ==============================================================================
@app.route('/api/menu', methods=['GET'])
@app.route('/api/c/get_menu', methods=['GET'])
def customer_get_menu():
    menu = MenuItem.query.filter_by(status='selling').order_by(MenuItem.category_id.asc()).order_by(MenuItem.rank_incat.asc()).all()
    menu_list = [item.to_dict() for item in menu]
    response = response_template(True, 200, 'Success: customer_get_menu()', menu_list)
    # response.headers['Cache-Control'] = 'public, max-age=604800'
    return response

@app.route('/api/category', methods=['GET'])
def get_category():
    category = Category.query.order_by(Category.rank.asc()).all()
    category_list = [item.to_dict() for item in category]
    return response_template(True, 200, 'Success: get_category()', category_list)

# staff can see 'hidden' menu items
@app.route('/api/s/menu/get_menu', methods=['GET'])
def staff_get_menu():
    menu = MenuItem.query.order_by(MenuItem.category_id.asc()).order_by(MenuItem.rank_incat.asc()).all()
    menu_list = [item.to_dict() for item in menu]
    response = response_template(True, 200, 'Success: staff_get_menu()', menu_list)
    # response.headers['Cache-Control'] = 'public, max-age=604800'
    return response

@app.route('/api/s/menu/get_menu/all', methods=['GET'])
def staff_get_menu_all():
    menu = MenuItem.query.order_by(MenuItem.category_id.asc()).order_by(MenuItem.rank_incat.asc()).all()
    menu_list = [item.to_dict() for item in menu]
    return response_template(True, 200, 'Success: staff_get_menu_all()', menu_list)

@app.route('/api/s/menu/get_menu/selling', methods=['GET'])
def staff_get_menu_selling():
    menu = MenuItem.query.filter_by(status='selling').order_by(MenuItem.category_id.asc()).order_by(MenuItem.rank_incat.asc()).all()
    menu_list = [item.to_dict() for item in menu]
    return response_template(True, 200, 'Success: staff_get_menu_selling()', menu_list)

@app.route('/api/s/menu/get_menu/hidden', methods=['GET'])
def staff_get_menu_hidden():
    menu = MenuItem.query.filter_by(status='hidden').order_by(MenuItem.category_id.asc()).order_by(MenuItem.rank_incat.asc()).all()
    menu_list = [item.to_dict() for item in menu]
    return response_template(True, 200, 'Success: staff_get_menu_hidden()', menu_list)

@app.route('/api/s/menu/add', methods=['POST'])
def menu_add_item():
    # image file processing
    image_url =  ''
    if 'file' not in request.files:
        return response_template(False, 400, 'No file part in the request', None)
    file = request.files['file']
    if file.filename == '':
        return response_template(False, 400, 'No file selected for uploading', None)
    if file:
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file.save(os.path.join(app.config['IMAGE_FOLDER'], unique_filename))
        image_url = IMAGE_PATH_PREFIX + unique_filename

    # item data processing
    data = request.form
    new_item = MenuItem(data['name'], data['category_id'], data['price'], 
                        data['description'], data['ingredients'], image_url, data['stock'])
    db.session.add(new_item)
    db.session.commit()
    return response_template(True, 200, 'New item created successfully', None)

@app.route('/api/s/menu/update/<item_id>', methods=['POST'])
def update_menu(item_id):
    # Ensure users are managers
    item = MenuItem.query.get(item_id)
    if not item:
        return response_template(True, 404, 'Menu item not found', None)

    data = request.get_json()

    item.name = data.get('name', item.name)
    item.description = data.get('description', item.description)
    item.price = data.get('price', item.price)
    item.category_id = data.get('category_id', item.category_id)
    item.ingredients = data.get('ingredients', item.ingredients)
    item.image_url = data.get('image_url', item.image_url)
    item.stock = data.get('stock', item.stock)
    item.status = data.get('status', item.status)
    item.rank_incat = data.get('rank_incat', item.rank_incat)

    try:
        db.session.commit()
        return response_template(True, 200, 'Menu item updated successfully', item.to_dict())
    except Exception as e:
        db.session.rollback()
        return response_template(False, 500, 'Failed to update menu item', {'error': str(e)})

@app.route('/api/s/menu/hide/<item_id>', methods=['POST'])
def hide_menu_item(item_id):
    item = MenuItem.query.get(item_id)
    if (item):
        item.status = 'hidden'
        db.session.commit()
        return response_template(True, 200, 'Hide item successfully', None)
    else:
        return response_template(False, 500, 'No such item', None)

@app.route('/api/s/menu/unhide/<item_id>', methods=['POST'])
def unhide_menu_item(item_id):
    item = MenuItem.query.get(item_id)
    if (item):
        item.status = 'selling'
        db.session.commit()
        return response_template(True, 200, 'Unhide item successfully', None)
    else:
        return response_template(False, 500, 'No such item', None)

@app.route('/api/s/menu/delete/<item_id>', methods=['POST'])
def delete_menu_item(item_id):
    item = MenuItem.query.get(item_id)
    if (item):
        db.session.delete(item)
        db.session.commit()
        return response_template(True, 200, 'Delete item successfully', None)
    else:
        return response_template(False, 500, 'No such item', None)

@app.route('/api/s/menu/item/rank', methods=['POST'])
def order_menu_item():
    items_list = request.get_json()
    print(items_list)
    for item in items_list:
        menu_item = MenuItem.query.get(item['item_id'])
        if (menu_item):
            print(menu_item)
            menu_item.rank_incat = item['rank_incat']
            print(menu_item.rank_incat)
            menu_item.category_id = item['category_id']
        else:
            return response_template(False, 500, 'Failed to get item: {}'.format(item['item_id']), None)

    try:
        db.session.commit()
        items_list = MenuItem.query.order_by(MenuItem.category_id.asc()).order_by(MenuItem.rank_incat.asc()).all()
        items_list = [item.to_dict() for item in items_list]
        return response_template(True, 200, 'MenuItems ordered successfully', items_list)
    except Exception as e:
        db.session.rollback()
        return response_template(False, 500, 'Failed to order menu items', {'error': str(e)})

# ==============================================================================
# =================================  Requests  =================================
# ==============================================================================
@app.route('/api/requests/new', methods=['POST'])
def create_request():
    data = request.get_json()
    new_request = Request(table_number=data['table_number'], request_type=data['request_type'])
    db.session.add(new_request)
    db.session.commit()
    res_data = {'request_id': new_request.id}
    return response_template(True, 201, 'Request Created', res_data)

@app.route('/api/requests/get', methods=['GET'])
def get_pending_requests():
    pending_requests = Request.query.filter_by(status='pending').order_by(Request.timestamp.asc()).all()
    req_list = [ req.to_dict() for req in pending_requests]
    return response_template(True, 200, 'Success', req_list)

@app.route('/api/requests/cancel/<int:request_id>', methods=['POST'])
def cancel_request(request_id):
    req = Request.query.get(request_id)
    if req and req.status != 'done':
        req.status = 'cancel'
        db.session.commit()
        return response_template(True, 200, 'Request Cancelled', None)
    else:
        return response_template(False, 500, 'Request does not exist or has been completed', None)

@app.route('/api/requests/complete/<int:request_id>', methods=['POST'])
def complete_request(request_id):
    req = Request.query.get(request_id)
    if req and req.status != 'done':
        req.status = 'done'
        db.session.commit()
        return response_template(True, 200, 'Request Completed', None)
    else:
        return response_template(False, 500, 'Request does not exist or has been completed', None)
    
# ==============================================================================
# =============================  Orders  =======================================
# ==============================================================================
@app.route('/api/order/new', methods=['POST'])
def create_order():
    data = request.json
    table_number = data['table_number']
    new_order = Order(table_number)
    db.session.add(new_order)
    
    total_price = 0
    for item in data['ordered_items']:
        item_id = item['id']
        menu_item = MenuItem.query.get(item_id)
        kitchen_item = KitchenOrderItem(menu_item.id, menu_item.name, table_number, item['quantity'], image_url=menu_item.image_url)
        db.session.add(kitchen_item)
        
        item_id = item['id']
        item_name = MenuItem.query.get(item_id).name
        order_item = OrderItem(order_id=new_order.id, item_id=item['id'], item_name=item_name, quantity=item['quantity'], price=item['price'])
        db.session.add(order_item)
        total_price += menu_item.price * item['quantity']
    
    new_order.subtotal = total_price
    try:
        db.session.commit()
        payload = {
            'order_id': new_order.id,
            'subtotal': new_order.subtotal
        }
        return response_template(True, 200, 'Order created successfully', payload)
    except Exception as e:
        db.session.rollback()
        return response_template(False, 500, 'Failed to create new order', {'error': str(e)})

@app.route('/api/order/checkout/<order_id>', methods=['POST'])
def order_checkout(order_id):
    order = Order.query.get(order_id)
    if (not order):
        return response_template(False, 500, 'No such order, id: {}'.format(order_id), None)
    if (order.status != 'ordering'):
        return response_template(False, 500, 'Invalid order status: {}'.format(order.status), None)
    order.status = 'checking'
    try:
        db.session.commit()
        return response_template(True, 200, 'Success: checkout', None)
    except Exception as e:
        db.session.rollback()
        return response_template(False, 500, 'Failed to checkout', {'error': str(e)})
    
@app.route('/api/order/get/all', methods=['GET'])
def get_all_order():
    order_list = Order.query.all()
    data =  [order.to_order() for order in order_list]
    return response_template(True, 200, 'Success Get all order', data)

@app.route('/api/order/get/<int:table_number>', methods=['GET'])
def get_table_order(table_number):
    # it is possible for the same table having more than 1 'checking' order
    # so we return all of them for the staff to choose from
    order_list = Order.query.filter_by(table_number=table_number).filter_by(status='checking').all()
    data =  [order.to_order() for order in order_list]
    return response_template(True, 200, 'Success Get table order', data)

@app.route('/api/order/complete/<int:order_id>', methods=['POST'])
def complete_order(order_id):
    order = Order.query.get(order_id)
    if order and order.status != 'paid' and order.status != 'deleted':
        order.status = 'paid'
        db.session.commit()
        return response_template(True, 200, 'Success complete order', None)
    else:
        return response_template(False, 500, 'Failed to complete order', None)
    
@app.route('/api/order/delete/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    order = Order.query.get(order_id)
    if order and order.status != 'deleted':
        order.status = 'deleted'
        db.session.commit()
        return response_template(True, 200, 'Success delete order', None)
    else:
        return response_template(False, 500, 'Failed to delete order', None)
    

# ==============================================================================
# =============================  Kitchen  ======================================
# ==============================================================================

@app.route('/api/s/kitchen/get_cooking_item', methods=['GET'])
def get_cooking_item():
    item_list = KitchenOrderItem.query.filter_by(status='cooking').order_by(KitchenOrderItem.timestamp.asc()).all()
    item_list = [item.to_dict() for item in item_list]
    return response_template(True, 200, 'Success get_cooking_item()', item_list)

@app.route('/api/s/kitchen/finish_cooking/<int:kitchen_order_item_id>', methods=['POST'])
def finish_cooking(kitchen_order_item_id):
    item = KitchenOrderItem.query.get(kitchen_order_item_id)
    if (item):
        item.status = 'ready'
        db.session.commit()
        return response_template(True, 200, 'Success finish_cooking()', None)
    else:
        return response_template(False, 500, 'No such item', None)

@app.route('/api/s/kitchen/get_ready_item', methods=['GET'])
def get_ready_item():
    item_list = KitchenOrderItem.query.filter_by(status='ready').order_by(KitchenOrderItem.timestamp.asc()).all()
    item_list = [item.to_dict() for item in item_list]
    return response_template(True, 200, 'Success get_ready_item()', item_list)

@app.route('/api/s/kitchen/finish_delivery/<int:kitchen_order_item_id>', methods=['POST'])
def finish_delivery(kitchen_order_item_id):
    item = KitchenOrderItem.query.get(kitchen_order_item_id)
    if (item):
        item.status = 'delivered'
        db.session.commit()
        return response_template(True, 200, 'Success finish_delivery()', None)
    else:
        return response_template(False, 500, 'No such item', None)