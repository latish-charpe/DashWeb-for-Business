import re

def update_index():
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Define User Management Section HTML
    user_mgmt_html = """
          <div class="settings-section">
            <h3>User Management</h3>
            <div class="user-management-table-container" style="overflow-x: auto; margin-top: 15px;">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Username</th>
                    <th>Password</th>
                    <th>Role</th>
                  </tr>
                </thead>
                <tbody id="user-mgmt-tbody">
                  <!-- Populated by JS -->
                  <tr><td colspan="4" style="text-align:center;">Loading users...</td></tr>
                </tbody>
              </table>
            </div>
          </div>
"""
    
    # Inject before <div class="settings-footer">
    if "<h3>User Management</h3>" not in content:
        content = content.replace('<div class="settings-footer">', f"{user_mgmt_html}\n          <div class=\"settings-footer\">")
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    update_index()
