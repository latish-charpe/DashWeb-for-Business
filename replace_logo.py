with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace desktop logo
old_desktop = '<span class="logo-initials">IH</span>'
new_desktop = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-top: 2px;"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>'
html = html.replace(old_desktop, new_desktop)

# Replace mobile logo
old_mobile = '<span class="logo-initials text-xs">IH</span>'
new_mobile = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-top: 2px;"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>'
html = html.replace(old_mobile, new_mobile)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Logos replaced successfully!")
