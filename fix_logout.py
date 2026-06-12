with open('app.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

logout_logic = """
const logoutBtn = document.getElementById('logoutBtn');
if (logoutBtn) {
  logoutBtn.addEventListener('click', (e) => {
    e.preventDefault();
    showToast('Signing out...', 'info');
    setTimeout(() => {
      window.location.reload();
    }, 1000);
  });
}
"""

if 'logoutBtn.addEventListener' not in js_content:
    js_content += logout_logic
    with open('app.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    print("Added logoutBtn logic")
else:
    print("Logic already exists")
