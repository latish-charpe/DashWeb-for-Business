import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

prices_dict = '''PRODUCT_PRICES = {
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
'''

# Insert dictionary after db = SQLAlchemy(app) if not already there
if 'PRODUCT_PRICES = {' not in content:
    content = content.replace('db = SQLAlchemy(app)', 'db = SQLAlchemy(app)\n\n' + prices_dict)

# Modify add_order
old_add_order = '''@app.route('/api/v1/orders/add', methods=['POST'])
def add_order():
    try:
        data = request.json
        amount = float(data.get('amount', 0))'''
new_add_order = '''@app.route('/api/v1/orders/add', methods=['POST'])
def add_order():
    try:
        data = request.json
        product = data.get('product')
        amount = float(PRODUCT_PRICES.get(product, data.get('amount', 0)))'''
content = content.replace(old_add_order, new_add_order)

# Modify upload_csv
old_upload_csv = '''            try:
                amt = float(row.get('Amount', 0))
            except:
                amt = 0.0'''
new_upload_csv = '''            try:
                prod = row.get('Product', '')
                amt = float(PRODUCT_PRICES.get(prod, row.get('Amount', 0)))
            except:
                amt = 0.0'''
content = content.replace(old_upload_csv, new_upload_csv)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('app.py updated with price enforcement')
