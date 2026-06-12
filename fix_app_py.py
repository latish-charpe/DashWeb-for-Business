with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re

old_margins_1 = '''        margins = {
            'Core Cloud Suite': 0.38,
            'CRM Enterprise': 0.32,
            'ThreatShield Guard': 0.35,
            'Integration Connect': 0.28
        }'''

new_margins_1 = '''        margins = {
            'Apple iPhone 16': 0.28,
            'Samsung Galaxy S25': 0.25,
            'OnePlus 14': 0.20,
            'MacBook Air M4': 0.35,
            'Dell XPS 15': 0.32,
            'Lenovo ThinkBook 16': 0.30,
            'iPad Air': 0.38,
            'Samsung Galaxy Tab S10': 0.34
        }'''

old_margins_2 = '''        margins = {
            'Core Cloud Suite': 0.38, 'CRM Enterprise': 0.32,
            'ThreatShield Guard': 0.35, 'Integration Connect': 0.28
        }'''

new_margins_2 = '''        margins = {
            'Apple iPhone 16': 0.28, 'Samsung Galaxy S25': 0.25,
            'OnePlus 14': 0.20, 'MacBook Air M4': 0.35,
            'Dell XPS 15': 0.32, 'Lenovo ThinkBook 16': 0.30,
            'iPad Air': 0.38, 'Samsung Galaxy Tab S10': 0.34
        }'''

old_fallback = '''        top_product = max(product_data, key=lambda x: float(x[1]), default=('Core Cloud Suite', 0))[0] if product_data else 'Core Cloud Suite''''
new_fallback = '''        top_product = max(product_data, key=lambda x: float(x[1]), default=('Apple iPhone 16', 0))[0] if product_data else 'Apple iPhone 16''''

old_action = '''            'action': f'Prioritize {top_product} upsell campaigns. Bundle Integration Connect with CRM Enterprise.','''
new_action = '''            'action': f'Prioritize {top_product} upsell campaigns. Bundle iPad Air with Apple iPhone 16.','''

content = content.replace(old_margins_1, new_margins_1)
content = content.replace(old_margins_2, new_margins_2)
content = content.replace(old_fallback, new_fallback)
content = content.replace(old_action, new_action)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('app.py updated')
