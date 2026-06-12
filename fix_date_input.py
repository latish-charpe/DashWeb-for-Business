import re

def fix_date_input():
    # 1. Update index.html
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # We need to change the label and the input type
    old_label = "<label>Date (DD/MM/YYYY)</label>"
    new_label = "<label>Date</label>"
    
    old_input = '<input type="text" class="form-control" id="orderDate" placeholder="e.g. 15/08/2026" required />'
    new_input = '<input type="date" class="form-control" id="orderDate" required />'

    if old_label in content:
        content = content.replace(old_label, new_label)
    if old_input in content:
        content = content.replace(old_input, new_input)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)

    # 2. Update app.js
    with open('app.js', 'r', encoding='utf-8') as f:
        js_content = f.read()

    old_js = "date: document.getElementById('orderDate').value"
    new_js = "date: document.getElementById('orderDate').value.split('-').reverse().join('/')"

    if old_js in js_content:
        js_content = js_content.replace(old_js, new_js)

    with open('app.js', 'w', encoding='utf-8') as f:
        f.write(js_content)

    print("Date input fixed successfully.")

if __name__ == '__main__':
    fix_date_input()
