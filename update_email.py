with open('app.py', 'r', encoding='utf-8') as f:
    py_content = f.read()

old_email = "'email': 'shrikant.keche@insighthub.com'"
new_email = "'email': 's.keche@skexecutive.com'"

py_content = py_content.replace(old_email, new_email)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(py_content)

print("Updated email in app.py")
