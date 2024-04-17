from sqlalchemy.exc import IntegrityError

def populate_tables():
    from app import db
    from app.models import StaffAdmin, MenuItem, Category, Request, Order, OrderItem

    db.session.query(StaffAdmin).delete()       # clear all existing rows
    staff_list = []
    staff_list.append(StaffAdmin(staff_id='m1', input_password='password'))
    staff_list.append(StaffAdmin(staff_id='s1', input_password='password'))
    staff_list.append(StaffAdmin(staff_id='s2', input_password='password'))
    staff_list.append(StaffAdmin(staff_id='s3', input_password='password'))
    db.session.add_all(staff_list)

    db.session.query(MenuItem).delete()       # clear all existing rows
    menu_item_list = [] 
    menu_item_list.append(MenuItem('food1', 1, 10, 'delicious food', 'cheese, bacon', '/static/images/1.jpg', 10, 'selling', 0))
    menu_item_list.append(MenuItem('food2', 1, 10, 'delicious food', 'cheese, bacon', '/static/images/2.jpg', 10, 'selling', 1))
    menu_item_list.append(MenuItem('drink1', 2, 10, 'delicious food', 'cheese, bacon', '/static/images/3.jpg', 10, 'selling', 2))
    menu_item_list.append(MenuItem('item1', 1, 10, 'delicious food', 'cheese, bacon', '/static/images/4.jpg', 10, 'selling', 3))
    menu_item_list.append(MenuItem('burger4', 3, 10, 'delicious food', 'cheese, bacon', '/static/images/5.jpg', 10, 'selling', 4))
    menu_item_list.append(MenuItem('food4', 4, 10, 'delicious food', 'cheese, bacon', '/static/images/6.jpg', 10, 'selling', 0))
    menu_item_list.append(MenuItem('food3', 2, 10, 'delicious food', 'cheese, bacon', '/static/images/7.jpg', 10, 'selling', 1))
    menu_item_list.append(MenuItem('drink6', 2, 10, 'delicious food', 'cheese, bacon', '/static/images/8.jpg', 10, 'selling', 2))
    menu_item_list.append(MenuItem('item7', 4, 10, 'delicious food', 'cheese, bacon', '/static/images/9.jpg', 10, 'selling', 3))
    menu_item_list.append(MenuItem('burger9', 4, 10, 'delicious food', 'cheese, bacon', '/static/images/9.jpg', 10, 'selling', 4))
    db.session.add_all(menu_item_list)

    db.session.query(Category).delete()       # clear all existing rows
    category_list = []
    category_list.append(Category('Chicken', 0))
    category_list.append(Category('Beef', 1))
    category_list.append(Category('Drink', 2))
    category_list.append(Category('Alcohol', 3))
    db.session.add_all(category_list)


    # Add more records as needed
    db.session.commit()

def clear_all_records():
    from app import db
    from app.models import StaffAdmin, MenuItem, Category, Request, Order, OrderItem, KitchenOrderItem
    db.session.query(StaffAdmin).delete()
    db.session.query(MenuItem).delete()
    db.session.query(Category).delete()
    db.session.query(Request).delete()
    db.session.query(Order).delete()
    db.session.query(OrderItem).delete()
    db.session.query(KitchenOrderItem).delete()
    db.session.commit()



