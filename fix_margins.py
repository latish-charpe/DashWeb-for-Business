with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re

old_margins_block_1 = '''        margins = {
            'Apple iPhone 16': 0.28,
            'Samsung Galaxy S25': 0.25,
            'OnePlus 14': 0.20,
            'MacBook Air M4': 0.35,
            'Dell XPS 15': 0.32,
            'Lenovo ThinkBook 16': 0.30,
            'iPad Air': 0.38,
            'Samsung Galaxy Tab S10': 0.34
        }'''

old_margins_block_2 = '''        margins = {
            'Apple iPhone 16': 0.28, 'Samsung Galaxy S25': 0.25,
            'OnePlus 14': 0.20, 'MacBook Air M4': 0.35,
            'Dell XPS 15': 0.32, 'Lenovo ThinkBook 16': 0.30,
            'iPad Air': 0.38, 'Samsung Galaxy Tab S10': 0.34
        }'''

new_margins = '''        margins = {
            'Apple iPhone 16': 0.28, 'Apple iPhone 16 Pro': 0.32,
            'Samsung Galaxy S25': 0.25, 'Samsung Galaxy S25 Ultra': 0.29,
            'OnePlus 14': 0.20, 'Google Pixel 10': 0.24,
            'MacBook Air M4': 0.35, 'MacBook Pro M4': 0.38,
            'Dell XPS 15': 0.32, 'HP Pavilion 15': 0.22,
            'Lenovo ThinkBook 16': 0.30, 'ASUS ROG Strix G16': 0.33,
            'iPad Air': 0.38, 'Samsung Galaxy Tab S10': 0.34,
            'Apple Watch Series 11': 0.40, 'Samsung Galaxy Watch 8': 0.35,
            'AirPods Pro 3': 0.45, 'Sony WH-1000XM6': 0.42,
            'JBL Flip 7': 0.30, 'Logitech MX Master 4': 0.50
        }'''

content = content.replace(old_margins_block_1, new_margins)
content = content.replace(old_margins_block_2, new_margins)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('app.py updated margins')
