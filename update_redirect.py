with open('app.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

js_content = js_content.replace("window.location.reload();", "window.location.href = 'login.html';")

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print("Updated app.js to redirect to login.html")
