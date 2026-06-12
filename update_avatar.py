import re

def update_avatar_logic():
    with open('app.js', 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the block inside loadProfileSettings where we update the DOM
    old_code = """      document.querySelector('.profile-name').textContent = settings.username || settings.name;
      document.querySelector('.user-full-name').textContent = 'Username: ' + (settings.username || settings.name) + (settings.role ? ' | Role: ' + settings.role : '');
      if (document.querySelector('.user-email')) {
        document.querySelector('.user-email').style.display = 'none';
      }
      const sidebarPanel = document.querySelector('.sidebar-user-panel .user-name');
      if (sidebarPanel) sidebarPanel.textContent = settings.username || settings.name;"""
      
    new_code = """      const displayUser = settings.username || settings.name || 'User';
      document.querySelector('.profile-name').textContent = displayUser;
      document.querySelector('.user-full-name').textContent = 'Username: ' + displayUser + (settings.role ? ' | Role: ' + settings.role : '');
      
      if (document.querySelector('.user-email')) {
        document.querySelector('.user-email').style.display = 'none';
      }
      
      const sidebarPanel = document.querySelector('.sidebar-user-panel .user-name');
      if (sidebarPanel) sidebarPanel.textContent = displayUser;

      // Calculate dynamic initials
      let initials = '??';
      if (displayUser.length >= 2) {
          initials = displayUser.substring(0, 2).toUpperCase();
      } else if (displayUser.length === 1) {
          initials = displayUser.substring(0, 1).toUpperCase();
      }
      
      // Update all avatar circles (navbar and sidebar)
      document.querySelectorAll('.avatar-circle').forEach(el => {
          el.textContent = initials;
      });"""

    if old_code in content:
        content = content.replace(old_code, new_code)
    else:
        print("Could not find the target code block in app.js!")

    with open('app.js', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    update_avatar_logic()
