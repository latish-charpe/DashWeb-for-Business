import re
from app import app, db, User

def update_db():
    with app.app_context():
        # Update existing users in the database
        u1 = User.query.filter_by(username='shrikant').first()
        if u1:
            u1.password = 'shrikant123'
            u1.full_name = 'shrikant'
        u2 = User.query.filter_by(username='manager').first()
        if u2:
            u2.password = 'manager123'
            u2.full_name = 'manager'
        u3 = User.query.filter_by(username='analyst').first()
        if u3:
            u3.password = 'analyst123'
            u3.full_name = 'analyst'
        db.session.commit()

def update_app_py():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Update global mock profile settings
    content = content.replace("'name': 'Shrikant Keche'", "'name': 'shrikant'")
    content = content.replace("'email': 's.keche@skexecutive.com'", "'email': 'shrikant@demo.com'")

    # Update seed users
    old_seed = """        demo_users = [
            User(username='shrikant', password='admin123', role='CEO', full_name='Shrikant Keche'),
            User(username='manager', password='manager123', role='Manager', full_name='Rahul Patil'),
            User(username='analyst', password='analyst123', role='Analyst', full_name='Priya Sharma')
        ]"""
    new_seed = """        demo_users = [
            User(username='shrikant', password='shrikant123', role='CEO', full_name='shrikant'),
            User(username='manager', password='manager123', role='Manager', full_name='manager'),
            User(username='analyst', password='analyst123', role='Analyst', full_name='analyst')
        ]"""
    content = content.replace(old_seed, new_seed)

    # Update get_settings to include username and remove personal name logic
    old_settings_get = """@app.route('/api/v1/settings', methods=['GET'])
def get_settings():
    user = User.query.get(session.get('user_id'))
    if user:
        return jsonify({
            'name': user.full_name,
            'email': f"{user.username}@skexecutive.com",
            'role': user.role
        })"""
    new_settings_get = """@app.route('/api/v1/settings', methods=['GET'])
def get_settings():
    user = User.query.get(session.get('user_id'))
    if user:
        return jsonify({
            'username': user.username,
            'name': user.username,
            'role': user.role
        })"""
    content = content.replace(old_settings_get, new_settings_get)

    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)

def update_app_js():
    with open('app.js', 'r', encoding='utf-8') as f:
        content = f.read()

    old_profile = """      document.querySelector('.profile-name').textContent = settings.name.split(' ')[0] + '.';
      document.querySelector('.user-full-name').textContent = settings.name + (settings.role ? ' (' + settings.role + ')' : '');
      document.querySelector('.user-email').textContent = settings.email;
      const sidebarPanel = document.querySelector('.sidebar-user-panel .user-name');
      if (sidebarPanel) sidebarPanel.textContent = settings.name;"""
    new_profile = """      document.querySelector('.profile-name').textContent = settings.username || settings.name;
      document.querySelector('.user-full-name').textContent = 'Username: ' + (settings.username || settings.name) + (settings.role ? ' | Role: ' + settings.role : '');
      if (document.querySelector('.user-email')) {
        document.querySelector('.user-email').style.display = 'none';
      }
      const sidebarPanel = document.querySelector('.sidebar-user-panel .user-name');
      if (sidebarPanel) sidebarPanel.textContent = settings.username || settings.name;"""
    
    content = content.replace(old_profile, new_profile)
    
    with open('app.js', 'w', encoding='utf-8') as f:
        f.write(content)

def update_index_html():
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    content = content.replace('Shrikant K.', 'shrikant')
    content = content.replace('Shrikant Keche', 'shrikant')
    content = content.replace('s.keche@skexecutive.com', 'shrikant@demo.com')

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    update_db()
    update_app_py()
    update_app_js()
    update_index_html()
    print("Updates complete.")
