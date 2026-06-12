import re

def move_vars():
    with open('app.js', 'r', encoding='utf-8') as f:
        content = f.read()

    content = re.sub(r'let ordersCurrentPage = \d+;\n?', '', content)
    content = re.sub(r'const ordersLimit = \d+;\n?', '', content)

    content = content.replace("document.addEventListener('DOMContentLoaded', () => {", "document.addEventListener('DOMContentLoaded', () => {\n  let ordersCurrentPage = 1;\n  const ordersLimit = 10;")

    with open('app.js', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    move_vars()
