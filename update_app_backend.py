import re

def update_backend():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Add imports
    if 'from flask import session' not in content:
        content = content.replace(
            "from flask import Flask, jsonify, request, send_from_directory, send_file",
            "from flask import Flask, jsonify, request, send_from_directory, send_file, session, redirect, url_for"
        )
    
    # Add configs
    if "app.config['PERMANENT_SESSION_LIFETIME']" not in content:
        config_block = """app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'super_secret_dashweb_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=15)
"""
        content = content.replace("app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False", config_block)

    # Add User Model
    if "class User(db.Model):" not in content:
        user_model = """class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)

"""
        content = content.replace("# --- Database Models ---", f"# --- Database Models ---\n{user_model}")

    # Add Seed and before_request before # --- API Endpoints ---
    if "def check_auth():" not in content:
        auth_block = """
with app.app_context():
    db.create_all()
    if User.query.count() == 0:
        demo_users = [
            User(username='shrikant', password='admin123', role='CEO', full_name='Shrikant Keche'),
            User(username='manager', password='manager123', role='Manager', full_name='Rahul Patil'),
            User(username='analyst', password='analyst123', role='Analyst', full_name='Priya Sharma')
        ]
        db.session.bulk_save_objects(demo_users)
        db.session.commit()

@app.before_request
def check_auth():
    allowed_routes = ['login', 'api_login', 'static']
    if request.endpoint in allowed_routes:
        return
        
    if request.path.endswith('.css') or request.path.endswith('.js') or request.path.endswith('.png') or request.path.endswith('.svg') or request.path.endswith('.jpg'):
        return

    if 'user_id' not in session:
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Unauthorized'}), 401
        return redirect('/login')
        
    session.permanent = True

"""
        content = content.replace("# --- API Endpoints ---", f"{auth_block}\n# --- API Endpoints ---")

    # Add login/logout routes right after API Endpoints
    if "@app.route('/login')" not in content:
        routes_block = """@app.route('/login')
def login():
    if 'user_id' in session:
        return redirect('/')
    return send_file('login.html')

@app.route('/api/v1/login', methods=['POST'])
def api_login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    
    if user and user.password == password:
        session['user_id'] = user.id
        return jsonify({'success': True, 'user': {'name': user.full_name, 'role': user.role}})
    return jsonify({'success': False, 'error': 'Invalid username or password'}), 401

@app.route('/api/v1/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/v1/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        result = []
        for u in users:
            result.append({
                'id': u.id,
                'username': u.username,
                'password': u.password,
                'role': u.role,
                'full_name': u.full_name
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

"""
        content = content.replace("# --- API Endpoints ---", f"# --- API Endpoints ---\n{routes_block}")

    # Replace get_settings logic
    old_settings_get = """@app.route('/api/v1/settings', methods=['GET'])
def get_settings():
    return jsonify(profile_settings)"""
    new_settings_get = """@app.route('/api/v1/settings', methods=['GET'])
def get_settings():
    user = User.query.get(session.get('user_id'))
    if user:
        return jsonify({
            'name': user.full_name,
            'email': f"{user.username}@skexecutive.com",
            'role': user.role
        })
    return jsonify({'error': 'User not found'}), 404"""
    
    if old_settings_get in content:
        content = content.replace(old_settings_get, new_settings_get)

    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    update_backend()
