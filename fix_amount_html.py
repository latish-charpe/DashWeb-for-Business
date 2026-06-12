with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_input = '<input type="number" id="amount" name="amount" class="form-input" required min="0" step="0.01">'
new_input = '<input type="number" id="amount" name="amount" class="form-input" required min="0" step="0.01" readonly style="background-color: #f3f4f6; cursor: not-allowed;">'

content = content.replace(old_input, new_input)
content = content.replace('app.js?v=3.6.0', 'app.js?v=3.7.0')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('index.html updated')
