with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Desktop old and new
old_desktop = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-top: 2px;"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>'

new_desktop = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="margin-top: 1px;"><path d="M3 3v18h18"></path><path d="M18 9l-5 5-3-3-4 4"></path><path d="M14 9h4v4"></path></svg>'

# Mobile old and new
old_mobile = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-top: 2px;"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>'

new_mobile = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="margin-top: 1px;"><path d="M3 3v18h18"></path><path d="M18 9l-5 5-3-3-4 4"></path><path d="M14 9h4v4"></path></svg>'

html = html.replace(old_desktop, new_desktop)
html = html.replace(old_mobile, new_mobile)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Logo changed to Analytics Wave successfully!")
