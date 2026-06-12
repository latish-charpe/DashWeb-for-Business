from app import app, db, Order

PRODUCT_PRICES = {
    'Apple iPhone 16': 79900,
    'Apple iPhone 16 Pro': 119900,
    'Samsung Galaxy S25': 74999,
    'Samsung Galaxy S25 Ultra': 129999,
    'OnePlus 14': 64999,
    'Google Pixel 10': 79999,
    'MacBook Air M4': 114900,
    'MacBook Pro M4': 169900,
    'Dell XPS 15': 185000,
    'HP Pavilion 15': 65000,
    'Lenovo ThinkBook 16': 75000,
    'ASUS ROG Strix G16': 145000,
    'iPad Air': 59900,
    'Samsung Galaxy Tab S10': 89999,
    'Apple Watch Series 11': 41900,
    'Samsung Galaxy Watch 8': 34999,
    'AirPods Pro 3': 24900,
    'Sony WH-1000XM6': 29990,
    'JBL Flip 7': 11999,
    'Logitech MX Master 4': 10995
}

with app.app_context():
    orders = Order.query.all()
    count = 0
    for order in orders:
        if order.product in PRODUCT_PRICES:
            order.amount = PRODUCT_PRICES[order.product]
            count += 1
    db.session.commit()
    print(f'Successfully updated {count} orders with exact market prices.')
