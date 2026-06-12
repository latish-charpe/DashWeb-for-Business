import re

def update_js():
    with open('app.js', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Global Fetch Interceptor
    fetch_interceptor = """
// --- Global Fetch Interceptor for Auth ---
const originalFetch = window.fetch;
window.fetch = async function() {
    const response = await originalFetch.apply(this, arguments);
    if (response.status === 401) {
        window.location.href = '/login?expired=1';
    }
    return response;
};

document.addEventListener('DOMContentLoaded', () => {
"""
    if "const originalFetch = window.fetch;" not in content:
        content = content.replace("document.addEventListener('DOMContentLoaded', () => {", fetch_interceptor)

    # 2. Update loadProfileSettings
    old_profile = """      document.querySelector('.user-full-name').textContent = settings.name;
      document.querySelector('.user-email').textContent = settings.email;
      document.querySelector('.sidebar-user-panel .user-name').textContent = settings.name;"""
      
    new_profile = """      document.querySelector('.user-full-name').textContent = settings.name + (settings.role ? ' (' + settings.role + ')' : '');
      document.querySelector('.user-email').textContent = settings.email;
      const sidebarPanel = document.querySelector('.sidebar-user-panel .user-name');
      if (sidebarPanel) sidebarPanel.textContent = settings.name;"""
      
    if old_profile in content:
        content = content.replace(old_profile, new_profile)

    # 3. Add loadUserManagement
    user_mgmt_js = """
  // Load User Management
  const loadUserManagement = async () => {
    try {
      const res = await fetch('/api/v1/users');
      if (res.ok) {
        const users = await res.json();
        const tbody = document.getElementById('user-mgmt-tbody');
        if (tbody) {
          tbody.innerHTML = users.map(u => `
            <tr>
              <td>${u.id}</td>
              <td class="font-mono">${u.username}</td>
              <td class="font-mono" style="color: var(--text-muted);">${u.password}</td>
              <td><span class="role-badge role-${u.role.toLowerCase()}">${u.role}</span></td>
            </tr>
          `).join('');
        }
      }
    } catch (e) {
      console.error('Failed to load users', e);
    }
  };
"""
    if "const loadUserManagement = async () => {" not in content:
        content = content.replace("// Settings modification", f"{user_mgmt_js}\n  // Settings modification")

    # Add loadUserManagement() to initialization
    if "loadUserManagement();" not in content:
        content = content.replace("loadProfileSettings();", "loadProfileSettings();\n  loadUserManagement();")

    # 4. Update logoutBtn logic
    # We first find the block and replace it using regex to be safe.
    logout_pattern = re.compile(r"const logoutBtn = document\.getElementById\('logoutBtn'\);.*?if \(logoutBtn\) \{.*?\}.*?\}", re.DOTALL)
    
    new_logout = """const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', async (e) => {
      e.preventDefault();
      showToast('Signing out...', 'info');
      try {
        await fetch('/api/v1/logout', { method: 'POST' });
        window.location.href = '/login';
      } catch (err) {
        window.location.href = '/login';
      }
    });
  }"""
    
    if "await fetch('/api/v1/logout'" not in content:
        content = logout_pattern.sub(new_logout, content)

    with open('app.js', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    update_js()
