with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('<div class="avatar-circle">SK</div>', '<div class="avatar-circle">--</div>')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
