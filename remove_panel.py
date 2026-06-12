with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

target = '''    <div class="sidebar-user-panel">
      <div class="user-avatar-wrapper">
        <div class="avatar-sm">SK</div>
        <div class="status-indicator online"></div>
      </div>
      <div class="user-details">
        <span class="user-name">Shrikant Keche</span>
        <span class="user-role">Chief Executive Officer</span>
      </div>
    </div>'''

if target in html:
    html = html.replace(target, '')
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("User panel removed successfully.")
else:
    print("Could not find the exact text block to remove.")
