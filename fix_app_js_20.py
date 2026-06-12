with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

old_products_array = "const products = ['Apple iPhone 16', 'Samsung Galaxy S25', 'OnePlus 14', 'MacBook Air M4', 'Dell XPS 15', 'Lenovo ThinkBook 16', 'iPad Air', 'Samsung Galaxy Tab S10'];"
new_products_array = "const products = ['Apple iPhone 16', 'Apple iPhone 16 Pro', 'Samsung Galaxy S25', 'Samsung Galaxy S25 Ultra', 'OnePlus 14', 'Google Pixel 10', 'MacBook Air M4', 'MacBook Pro M4', 'Dell XPS 15', 'HP Pavilion 15', 'Lenovo ThinkBook 16', 'ASUS ROG Strix G16', 'iPad Air', 'Samsung Galaxy Tab S10', 'Apple Watch Series 11', 'Samsung Galaxy Watch 8', 'AirPods Pro 3', 'Sony WH-1000XM6', 'JBL Flip 7', 'Logitech MX Master 4'];"

content = content.replace(old_products_array, new_products_array)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("app.js updated")
