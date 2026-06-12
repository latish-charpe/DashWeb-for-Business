with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the bad logoutBtn logic at the end
bad_logic = """
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
content = content.replace(bad_logic, '')

# Add it just before the auto-refresh loop (inside DOMContentLoaded)
good_logic = """
  // --- Profile Dropdown Actions ---
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

loop_idx = content.find('// --- Real-time 5-Second Auto-Refresh Loop ---')
content = content[:loop_idx] + good_logic + content[loop_idx:]

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Moved logoutBtn logic inside DOMContentLoaded")
