import csv
import io
import uuid
import os
import datetime as dt_module
from flask import Flask, jsonify, request, send_from_directory, send_file, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

# ---------------------------------------------------------------------------
# Database URL: required in production (set as Render environment variable).
# Falls back to local dev DB only when DATABASE_URL is not set.
# ---------------------------------------------------------------------------
_DATABASE_URL = os.environ.get('DATABASE_URL')
if not _DATABASE_URL:
    # Local development fallback — NEVER used on Render
    import warnings
    warnings.warn(
        "DATABASE_URL environment variable is not set. "
        "Using local development database. "
        "Set DATABASE_URL on Render before deploying.",
        RuntimeWarning
    )
    _DATABASE_URL = 'mysql+mysqlconnector://root:root%40123@127.0.0.1:3306/insighthub'

# ---------------------------------------------------------------------------
# SECRET_KEY: must be set in production for secure sessions.
# ---------------------------------------------------------------------------
_SECRET_KEY = os.environ.get('SECRET_KEY')
if not _SECRET_KEY:
    import secrets
    _SECRET_KEY = secrets.token_hex(32)
    import warnings
    warnings.warn(
        "SECRET_KEY environment variable is not set. "
        "A random key was generated — sessions will NOT persist across restarts. "
        "Set SECRET_KEY on Render before deploying.",
        RuntimeWarning
    )

app = Flask(__name__, static_folder='.', static_url_path='')
app.config['SQLALCHEMY_DATABASE_URI'] = _DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 280,       # Recycle connections before Render's 5-min idle timeout
    'pool_pre_ping': True,     # Verify connection health before using from pool
    'pool_size': 5,
    'max_overflow': 10,
}
app.secret_key = _SECRET_KEY
app.config['PERMANENT_SESSION_LIFETIME'] = dt_module.timedelta(minutes=30)

db = SQLAlchemy(app)

PRODUCT_PRICES = {
    'Apple iPhone 16': 79900,
    'Apple iPhone 16 Pro': 119900,
    'Samsung Galaxy S25': 74999,
    'Samsung Galaxy S25 Ultra': 129999,
    'OnePlus 14': 64999,
    'Google Pixel 10': 79999,
    'MacBook Air M4': 114900,
    'MacBook Pro M4': 169900,
    'Dell XPS 15': 185000,
    'HP Pavilion 15': 65000,
    'Lenovo ThinkBook 16': 75000,
    'ASUS ROG Strix G16': 145000,
    'iPad Air': 59900,
    'Samsung Galaxy Tab S10': 89999,
    'Apple Watch Series 11': 41900,
    'Samsung Galaxy Watch 8': 34999,
    'AirPods Pro 3': 24900,
    'Sony WH-1000XM6': 29990,
    'JBL Flip 7': 11999,
    'Logitech MX Master 4': 10995
}


# --- Database Models ---
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    product = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    region = db.Column(db.String(50), nullable=False)
    month = db.Column(db.String(50), nullable=False)
    segment = db.Column(db.String(50), nullable=False)


class UploadHistory(db.Model):
    __tablename__ = 'upload_history'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    file_name = db.Column(db.String(200), nullable=False)
    upload_date = db.Column(db.String(50), nullable=False)
    records_imported = db.Column(db.Integer, nullable=False)
    uploaded_by = db.Column(db.String(100), nullable=False)

class Alert(db.Model):
    __tablename__ = 'alerts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    tag = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    desc = db.Column(db.Text, nullable=False)

class Activity(db.Model):
    __tablename__ = 'activities'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.Text, nullable=False)
    time = db.Column(db.String(50), nullable=False)

# Global variables for profile settings (mock persistence)
profile_settings = {
    'name': 'shrikant',
    'email': 'shrikant@demo.com'
}



# --- Helper Query Filtering Builder ---
def get_period_bounds(period):
    anchor = dt_module.date(2026, 6, 12)
    if period == 'daily':
        return anchor, anchor
    elif period == 'weekly':
        start = anchor - dt_module.timedelta(days=anchor.weekday())
        end = start + dt_module.timedelta(days=6)
        return start, end
    elif period == 'monthly':
        start = dt_module.date(anchor.year, anchor.month, 1)
        if anchor.month == 12:
            end = dt_module.date(anchor.year, 12, 31)
        else:
            end = dt_module.date(anchor.year, anchor.month + 1, 1) - dt_module.timedelta(days=1)
        return start, end
    elif period == 'quarterly':
        q_num = (anchor.month - 1) // 3 + 1
        q_start_month = (q_num - 1) * 3 + 1
        start = dt_module.date(anchor.year, q_start_month, 1)
        if q_start_month + 3 > 12:
            end = dt_module.date(anchor.year, 12, 31)
        else:
            end = dt_module.date(anchor.year, q_start_month + 3, 1) - dt_module.timedelta(days=1)
        return start, end
    elif period == 'yearly':
        start = dt_module.date(anchor.year, 1, 1)
        end = dt_module.date(anchor.year, 12, 31)
        return start, end
    return None, None

def get_previous_period_bounds(period):
    anchor = dt_module.date(2026, 6, 12)
    if period == 'daily':
        prev = anchor - dt_module.timedelta(days=1)
        return prev, prev
    elif period == 'weekly':
        curr_start = anchor - dt_module.timedelta(days=anchor.weekday())
        start = curr_start - dt_module.timedelta(days=7)
        end = start + dt_module.timedelta(days=6)
        return start, end
    elif period == 'monthly':
        if anchor.month == 1:
            start = dt_module.date(anchor.year - 1, 12, 1)
            end = dt_module.date(anchor.year - 1, 12, 31)
        else:
            start = dt_module.date(anchor.year, anchor.month - 1, 1)
            end = dt_module.date(anchor.year, anchor.month, 1) - dt_module.timedelta(days=1)
        return start, end
    elif period == 'quarterly':
        q_num = (anchor.month - 1) // 3 + 1
        if q_num == 1:
            start = dt_module.date(anchor.year - 1, 10, 1)
            end = dt_module.date(anchor.year - 1, 12, 31)
        else:
            prev_q_start_month = (q_num - 2) * 3 + 1
            start = dt_module.date(anchor.year, prev_q_start_month, 1)
            end = dt_module.date(anchor.year, prev_q_start_month + 3, 1) - dt_module.timedelta(days=1)
        return start, end
    elif period == 'yearly':
        start = dt_module.date(anchor.year - 1, 1, 1)
        end = dt_module.date(anchor.year - 1, 12, 31)
        return start, end
    return None, None

def get_filtered_query(exclude_params=None):
    if exclude_params is None:
        exclude_params = []
    elif isinstance(exclude_params, str):
        exclude_params = [exclude_params]
        
    region = request.args.get('region')
    month = request.args.get('month')
    segment = request.args.get('segment')
    product = request.args.get('product')
    period = request.args.get('period')
    
    q = Order.query
    if 'region' not in exclude_params and region and region not in ['null', 'undefined', 'all', 'All Products', 'All Status']:
        q = q.filter(Order.region == region)
    if 'month' not in exclude_params and month and month not in ['null', 'undefined', 'all']:
        q = q.filter(Order.month == month)
    if 'segment' not in exclude_params and segment and segment not in ['null', 'undefined', 'all']:
        q = q.filter(Order.segment == segment)
    if 'product' not in exclude_params and product and product not in ['null', 'undefined', 'all', 'All Products']:
        q = q.filter(Order.product == product)
        
    # Apply period date filter if not excluded AND month is not explicitly filtered
    if 'period' not in exclude_params and period and period != 'null' and period != 'undefined':
        if not month or month == 'null' or month == 'undefined' or 'month' in exclude_params:
            start_date, end_date = get_period_bounds(period)
            if start_date and end_date:
                q = q.filter(func.str_to_date(Order.date, '%d/%m/%Y').between(start_date, end_date))
                
    return q


with app.app_context():
    db.create_all()
    if User.query.count() == 0:
        demo_users = [
            User(username='shrikant', password='shrikant123', role='CEO', full_name='Shrikant Keche'),
            User(username='manager', password='manager123', role='Manager', full_name='Manager'),
            User(username='analyst', password='analyst123', role='Analyst', full_name='Analyst')
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


# --- API Endpoints ---

@app.route('/api/v1/orders/add', methods=['POST'])
def add_order():
    try:
        data = request.json
        product = data.get('product')
        amount = float(PRODUCT_PRICES.get(product, data.get('amount', 0)))
        date_str = data.get('date') # Expected DD/MM/YYYY
        
        # Calculate month from date
        try:
            dt = dt_module.datetime.strptime(date_str, '%d/%m/%Y')
            month = dt.strftime('%b')  # 'Jul', 'Aug', etc.
        except Exception:
            month = 'Jan'
            
        new_order = Order(
            id=f"ORD-{uuid.uuid4().hex[:8].upper()}",
            name=data.get('name'),
            product=data.get('product'),
            amount=amount,
            status=data.get('status'),
            date=date_str,
            region=data.get('region'),
            month=month,
            segment='New Clients' # Default segment
        )
        db.session.add(new_order)
        db.session.commit()
        return jsonify({'success': True, 'order_id': new_order.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route('/api/v1/orders/upload', methods=['POST'])
def upload_orders():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.DictReader(stream)
        
        success_count = 0
        failed_count = 0
        total_count = 0
        
        for row in csv_input:
            total_count += 1
            try:
                # Expected: Customer Name,Product,Amount,Region,Status,Date
                amt = float(row.get('Amount', 0))
                date_str = row.get('Date', '')
                
                try:
                    dt = dt_module.datetime.strptime(date_str, '%d/%m/%Y')
                    month = dt.strftime('%b')
                except Exception:
                    month = 'Jan'

                new_order = Order(
                    id=f"ORD-{uuid.uuid4().hex[:8].upper()}",
                    name=row.get('Customer Name'),
                    product=row.get('Product'),
                    amount=amt,
                    status=row.get('Status'),
                    date=date_str,
                    region=row.get('Region'),
                    month=month,
                    segment='New Clients'
                )
                db.session.add(new_order)
                success_count += 1
            except Exception as row_e:
                failed_count += 1
                
        # Record history
        user_id = session.get('user_id')
        user = User.query.get(user_id) if user_id else None
        uploader = user.username if user else 'System'
        
        history = UploadHistory(
            file_name=file.filename,
            upload_date=dt_module.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            records_imported=success_count,
            uploaded_by=uploader
        )
        db.session.add(history)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'total': total_count,
            'successful': success_count,
            'failed': failed_count
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/data/orders', methods=['GET'])
def get_data_orders():
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        search = request.args.get('search', '').lower()
        sort_by = request.args.get('sort_by', 'date')
        order_dir = request.args.get('order', 'desc')
        
        query = Order.query
        
        if search:
            query = query.filter(
                (Order.name.ilike(f'%{search}%')) |
                (Order.product.ilike(f'%{search}%')) |
                (Order.id.ilike(f'%{search}%')) |
                (Order.region.ilike(f'%{search}%'))
            )
            
        # Basic sorting mapping
        if sort_by == 'amount':
            col = Order.amount
        elif sort_by == 'name':
            col = Order.name
        elif sort_by == 'date':
            col = Order.id # Fallback to ID for descending date insertion
        else:
            col = Order.id
            
        if order_dir == 'desc':
            query = query.order_by(col.desc())
        else:
            query = query.order_by(col.asc())
            
        total = query.count()
        orders = query.offset((page - 1) * limit).limit(limit).all()
        
        data = [{
            'id': o.id,
            'name': o.name,
            'product': o.product,
            'amount': float(o.amount),
            'status': o.status,
            'date': o.date,
            'region': o.region
        } for o in orders]
        
        return jsonify({
            'data': data,
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/data/history', methods=['GET'])
def get_upload_history():
    try:
        history = UploadHistory.query.order_by(UploadHistory.id.desc()).limit(10).all()
        data = [{
            'id': h.id,
            'file_name': h.file_name,
            'upload_date': h.upload_date,
            'records_imported': h.records_imported,
            'uploaded_by': h.uploaded_by
        } for h in history]
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/login')
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



@app.route('/')
def index_route():
    return send_file('index.html')

@app.route('/api/v1/analytics', methods=['GET'])
def get_analytics():
    try:
        q = get_filtered_query()
        # Segment Analysis
        segments = db.session.query(Order.segment, func.sum(Order.amount)).group_by(Order.segment).all()
        segment_data = [{'segment': s[0], 'revenue': float(s[1])} for s in segments]
        
        # Product Trends
        products = db.session.query(Order.product, func.sum(Order.amount)).group_by(Order.product).all()
        product_data = [{'product': p[0], 'revenue': float(p[1])} for p in products]
        
        # Monthly Performance
        months_order = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        monthly_rev = db.session.query(Order.month, func.sum(Order.amount)).group_by(Order.month).all()
        monthly_map = {m[0]: float(m[1]) for m in monthly_rev}
        monthly_data = [{'month': m, 'revenue': monthly_map.get(m, 0.0)} for m in months_order]
        
        return jsonify({
            'segments': segment_data,
            'products': product_data,
            'monthly': monthly_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/metrics', methods=['GET'])
def get_metrics():
    try:
        q = get_filtered_query()
        
        # Revenue
        rev_val = q.with_entities(func.sum(Order.amount)).scalar()
        revenue = float(rev_val) if rev_val is not None else 0.0
        
        # Sales Count & Orders Count
        sales = q.count()
        orders = sales
        
        # Unique Customers Count
        customers = q.with_entities(func.count(func.distinct(Order.name))).scalar() or 0
        
        # Dynamic Profit Margin calculation based on product mix
        margins = {
            'Apple iPhone 16': 0.28, 'Apple iPhone 16 Pro': 0.32,
            'Samsung Galaxy S25': 0.25, 'Samsung Galaxy S25 Ultra': 0.29,
            'OnePlus 14': 0.20, 'Google Pixel 10': 0.24,
            'MacBook Air M4': 0.35, 'MacBook Pro M4': 0.38,
            'Dell XPS 15': 0.32, 'HP Pavilion 15': 0.22,
            'Lenovo ThinkBook 16': 0.30, 'ASUS ROG Strix G16': 0.33,
            'iPad Air': 0.38, 'Samsung Galaxy Tab S10': 0.34,
            'Apple Watch Series 11': 0.40, 'Samsung Galaxy Watch 8': 0.35,
            'AirPods Pro 3': 0.45, 'Sony WH-1000XM6': 0.42,
            'JBL Flip 7': 0.30, 'Logitech MX Master 4': 0.50
        }
        
        orders_list = q.all()
        total_profit = sum(float(o.amount) * margins.get(o.product, 0.347) for o in orders_list)
        profit = (total_profit / revenue * 100) if revenue > 0 else 34.7
        
        # Dynamic growth calculation: Period-over-period revenue growth
        period = request.args.get('period', 'monthly')
        month = request.args.get('month')
        
        q_base = get_filtered_query(exclude_params=['period'])
        
        if not month or month == 'null' or month == 'undefined':
            curr_start, curr_end = get_period_bounds(period)
            prev_start, prev_end = get_previous_period_bounds(period)
            
            curr_rev = revenue
            
            if prev_start and prev_end:
                prev_q = q_base.filter(func.str_to_date(Order.date, '%d/%m/%Y').between(prev_start, prev_end))
                prev_rev_val = prev_q.with_entities(func.sum(Order.amount)).scalar()
                prev_rev = float(prev_rev_val) if prev_rev_val is not None else 0.0
            else:
                prev_rev = 0.0
                
            if prev_rev > 0:
                growth = ((curr_rev - prev_rev) / prev_rev) * 100
            else:
                growth = 18.3 if curr_rev > 0 else 0.0
        else:
            # Month-over-month growth comparing to previous month in fiscal sequence
            months_seq = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            try:
                idx = months_seq.index(month)
                if idx > 0:
                    prev_month = months_seq[idx - 1]
                    q_base_mom = get_filtered_query(exclude_params=['month', 'period'])
                    prev_q = q_base_mom.filter(Order.month == prev_month)
                    prev_rev_val = prev_q.with_entities(func.sum(Order.amount)).scalar()
                    prev_rev = float(prev_rev_val) if prev_rev_val is not None else 0.0
                    if prev_rev > 0:
                        growth = ((revenue - prev_rev) / prev_rev) * 100
                    else:
                        growth = 18.3 if revenue > 0 else 0.0
                else:
                    growth = 18.3
            except ValueError:
                growth = 18.3
                
        # Dynamic NPS calculation (Delivered as Promoters, Pending as Detractors)
        delivered_count = q.filter(Order.status == 'Delivered').count()
        pending_count = q.filter(Order.status == 'Pending').count()
        nps_total = q.count()
        
        if nps_total > 0:
            nps = ((delivered_count - pending_count) / nps_total) * 100
        else:
            nps = 78.0
            
        # Previous period NPS for change calculation
        prev_nps = 73.8
        if not month or month == 'null' or month == 'undefined':
            curr_start, curr_end = get_period_bounds(period)
            prev_start, prev_end = get_previous_period_bounds(period)
            if prev_start and prev_end:
                prev_nps_q = q_base.filter(func.str_to_date(Order.date, '%d/%m/%Y').between(prev_start, prev_end))
                p_delivered = prev_nps_q.filter(Order.status == 'Delivered').count()
                p_pending = prev_nps_q.filter(Order.status == 'Pending').count()
                p_total = prev_nps_q.count()
                if p_total > 0:
                    prev_nps = ((p_delivered - p_pending) / p_total) * 100
        else:
            months_seq = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            try:
                idx = months_seq.index(month)
                if idx > 0:
                    prev_month = months_seq[idx - 1]
                    q_base_mom = get_filtered_query(exclude_params=['month', 'period'])
                    prev_nps_q = q_base_mom.filter(Order.month == prev_month)
                    p_delivered = prev_nps_q.filter(Order.status == 'Delivered').count()
                    p_pending = prev_nps_q.filter(Order.status == 'Pending').count()
                    p_total = prev_nps_q.count()
                    if p_total > 0:
                        prev_nps = ((p_delivered - p_pending) / p_total) * 100
            except ValueError:
                pass
                
        nps_change = nps - prev_nps
        
        # --- NEW DASHBOARD METRICS ---
        top_product_row = q.with_entities(Order.product, func.count(Order.id)).group_by(Order.product).order_by(func.count(Order.id).desc()).first()
        if top_product_row:
            top_product_name, top_product_units = top_product_row
        else:
            top_product_name, top_product_units = 'N/A', 0
            
        aov = revenue / orders if orders > 0 else 0
        
        completed_orders = q.filter(Order.status.in_(['Completed', 'Delivered'])).count()
        pending_orders = pending_count
        
        # --- AI BUSINESS HEALTH SCORE ENGINE ---
        if orders > 0:
            score = 0
            # 1. Profit Margin (max 30 pts)
            score += min(30, profit * 1.5)
            # 2. Revenue Growth (max 20 pts)
            score += min(20, max(0, growth))
            # 3. Completed Order Percentage (max 30 pts)
            completed_pct = (completed_orders / orders) * 100
            score += completed_pct * 0.3
            # 4. Customer ratio (max 10 pts)
            score += min(10, (customers / orders) * 20)
            # 5. Pending Penalty
            pending_pct = (pending_orders / orders) * 100
            score += max(0, 10 - (pending_pct * 0.5))
            health_score = min(100, max(0, round(score)))
        else:
            health_score = None
            
        return jsonify({
            'revenue': revenue,
            'sales': sales,
            'customers': customers,
            'orders': orders,
            'profit': profit,
            'growth': growth,
            'nps': nps,
            'npsChange': nps_change,
            'topProduct': top_product_name,
            'topProductUnits': top_product_units,
            'aov': aov,
            'completedOrders': completed_orders,
            'pendingOrders': pending_orders,
            'healthScore': health_score
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/orders', methods=['GET'])
def get_orders():
    try:
        q = get_filtered_query()
        
        # Filters
        status_filter = request.args.get('status')
        if status_filter and status_filter != 'all':
            q = q.filter(Order.status == status_filter)
            
        product_filter = request.args.get('product')
        if product_filter and product_filter != 'all':
            q = q.filter(Order.product == product_filter)
            
        # Date Range Filter
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        if start_date_str and end_date_str:
            try:
                # Assuming UI sends YYYY-MM-DD
                q = q.filter(func.str_to_date(Order.date, '%d/%m/%Y').between(start_date_str, end_date_str))
            except:
                pass
                
        # Search
        search_query = request.args.get('search')
        if search_query:
            search_query = f"%{search_query}%"
            q = q.filter(
                (Order.name.ilike(search_query)) |
                (Order.product.ilike(search_query)) |
                (Order.id.ilike(search_query)) |
                (Order.region.ilike(search_query))
            )
            
        # Sorting
        sort_by = request.args.get('sort_by', 'date')
        order_dir = request.args.get('order', 'desc')
        
        if sort_by == 'amount':
            col = Order.amount
        elif sort_by == 'date':
            col = Order.id # Fallback to ID for descending date insertion
        elif sort_by == 'name':
            col = Order.name
        else:
            col = Order.id
            
        if order_dir == 'desc':
            q = q.order_by(col.desc())
        else:
            q = q.order_by(col.asc())
            
        # Pagination
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        total = q.count()
        
        orders_list = q.offset((page - 1) * limit).limit(limit).all()
        
        result = []
        for o in orders_list:
            result.append({
                'id': o.id,
                'name': o.name,
                'product': o.product,
                'amount': float(o.amount),
                'status': o.status,
                'date': o.date,
                'region': o.region,
                'month': o.month,
                'segment': o.segment
            })
        return jsonify({
            'data': result,
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/orders/process', methods=['POST'])
def process_order():
    try:
        data = request.json or {}
        order_id = data.get('order_id')
        if not order_id:
            return jsonify({'error': 'Order ID is required'}), 400
            
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
            
        old_status = order.status
        if old_status == 'Processing':
            order.status = 'Delivered'
            new_status = 'Delivered'
        elif old_status == 'Pending':
            order.status = 'Processing'
            new_status = 'Processing'
        else:
            new_status = old_status
            
        db.session.commit()
        
        # Add timeline activity
        act = Activity(
            title="Order Processed",
            desc=f"Transaction {order_id} status updated from {old_status} to {new_status}.",
            time="Just now"
        )
        db.session.add(act)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'id': order_id,
            'new_status': new_status
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/alerts', methods=['GET'])
def get_alerts():
    try:
        alerts = Alert.query.all()
        result = []
        for a in alerts:
            result.append({
                'id': a.id,
                'title': a.title,
                'tag': a.tag,
                'type': a.type,
                'desc': a.desc
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/alerts/<int:alert_id>/status', methods=['POST'])
def update_alert_status(alert_id):
    try:
        alert = Alert.query.get(alert_id)
        if not alert:
            return jsonify({'error': 'Alert not found'}), 404
            
        data = request.json or {}
        if 'type' in data:
            alert.type = data['type']
        if 'title' in data:
            alert.title = data['title']
        if 'desc' in data:
            alert.desc = data['desc']
            
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/products', methods=['GET'])
def get_products():
    try:
        products_query = db.session.query(Order.product).distinct().order_by(Order.product).all()
        products = [p[0] for p in products_query if p[0]]
        return jsonify(products)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/activities', methods=['GET'])
def get_activities():
    try:
        # Fetch latest 10 activities
        acts = Activity.query.order_by(Activity.id.desc()).limit(10).all()
        result = []
        for a in acts:
            result.append({
                'id': a.id,
                'title': a.title,
                'desc': a.desc,
                'time': a.time
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_chart_categories_and_orders(q, period, month_filter):
    anchor = dt_module.date(2026, 6, 12)
    days_in_month = {
        'Jan': 31, 'Feb': 28, 'Mar': 31, 'Apr': 30, 'May': 31, 'Jun': 30,
        'Jul': 31, 'Aug': 31, 'Sep': 30, 'Oct': 31, 'Nov': 30, 'Dec': 31
    }
    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }
    
    if month_filter and month_filter != 'null' and month_filter != 'undefined':
        num_days = days_in_month.get(month_filter[:3], 30)
        categories = [f"{i:02d} {month_filter[:3]}" for i in range(1, num_days + 1)]
        orders = q.all()
        
        def map_order_to_cat(o):
            try:
                parts = o.date.split('/')
                day = int(parts[0])
                if 1 <= day <= len(categories):
                    return categories[day - 1]
            except:
                pass
            return None
            
        return categories, orders, map_order_to_cat

    if period == 'daily' or period == 'weekly':
        week_start = anchor - dt_module.timedelta(days=anchor.weekday())
        categories = []
        for i in range(7):
            d = week_start + dt_module.timedelta(days=i)
            categories.append(d.strftime('%d %b'))
            
        orders = q.all()
        
        def map_order_to_cat(o):
            try:
                d = dt_module.datetime.strptime(o.date, '%d/%m/%Y').date()
                if week_start <= d <= week_start + dt_module.timedelta(days=6):
                    return d.strftime('%d %b')
            except:
                pass
            return None
            
        return categories, orders, map_order_to_cat
        
    elif period == 'monthly':
        categories = [f"{i:02d} Jun" for i in range(1, 31)]
        orders = q.all()
        
        def map_order_to_cat(o):
            try:
                parts = o.date.split('/')
                day = int(parts[0])
                month_num = int(parts[1])
                if month_num == 6 and 1 <= day <= 30:
                    return categories[day - 1]
            except:
                pass
            return None
            
        return categories, orders, map_order_to_cat
        
    elif period == 'quarterly':
        categories = ['Apr', 'May', 'Jun']
        orders = q.all()
        
        def map_order_to_cat(o):
            try:
                month_num = int(o.date.split('/')[1])
                name = month_names.get(month_num)
                if name in categories:
                    return name
            except:
                pass
            return None
            
        return categories, orders, map_order_to_cat
        
    elif period == 'yearly':
        categories = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        orders = q.all()
        
        def map_order_to_cat(o):
            try:
                month_num = int(o.date.split('/')[1])
                name = month_names.get(month_num)
                if name in categories:
                    return name
            except:
                pass
            return None
            
        return categories, orders, map_order_to_cat

    categories = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    orders = q.all()
    def map_order_to_cat(o):
        try:
            month_num = int(o.date.split('/')[1])
            return month_names.get(month_num)
        except:
            pass
        return None
    return categories, orders, map_order_to_cat


@app.route('/api/v1/chart/sales', methods=['GET'])
def get_chart_sales():
    try:
        q = get_filtered_query()
        period = request.args.get('period', 'monthly')
        month_filter = request.args.get('month')
        
        categories, orders, map_func = get_chart_categories_and_orders(q, period, month_filter)
        
        counts = {cat: 0 for cat in categories}
        for o in orders:
            cat = map_func(o)
            if cat in counts:
                counts[cat] += 1
                
        data = [counts[cat] for cat in categories]
        return jsonify({
            'categories': categories,
            'data': data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/chart/region', methods=['GET'])
def get_chart_region():
    try:
        q = get_filtered_query(exclude_params=['region'])
        regions = ['Maharashtra', 'Gujarat', 'Karnataka', 'Telangana', 'Delhi']
        
        db_regs = q.with_entities(Order.region, func.sum(Order.amount)).group_by(Order.region).all()
        region_map = {r: 0.0 for r in regions}
        for r_name, amt in db_regs:
            if r_name in region_map:
                region_map[r_name] = float(amt)
                
        total = sum(region_map.values())
        if total > 0:
            series = [round((region_map[r] / total) * 100, 1) for r in regions]
        else:
            series = [0.0 for r in regions]
            
        return jsonify({
            'labels': regions,
            'series': series,
            'amounts': [region_map[r] for r in regions]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/chart/customers', methods=['GET'])
def get_chart_customers():
    try:
        q = get_filtered_query(exclude_params=['segment'])
        period = request.args.get('period', 'monthly')
        month_filter = request.args.get('month')
        
        categories, orders, map_func = get_chart_categories_and_orders(q, period, month_filter)
        
        new_counts = {cat: 0 for cat in categories}
        ret_counts = {cat: 0 for cat in categories}
        for o in orders:
            cat = map_func(o)
            if cat:
                if o.segment == 'New Clients':
                    new_counts[cat] += 1
                else:
                    ret_counts[cat] += 1
                    
        return jsonify({
            'categories': categories,
            'new_clients': [new_counts[cat] for cat in categories],
            'returning': [ret_counts[cat] for cat in categories]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/v1/chart/profit', methods=['GET'])
def get_chart_profit():
    try:
        q = get_filtered_query()
        period = request.args.get('period', 'monthly')
        month_filter = request.args.get('month')
        
        categories, orders, map_func = get_chart_categories_and_orders(q, period, month_filter)
        
        rev_map = {cat: 0.0 for cat in categories}
        for o in orders:
            cat = map_func(o)
            if cat:
                rev_map[cat] += float(o.amount)
                
        revenue_series = [round(rev_map[cat], 2) for cat in categories]
        expense_series = [round(r * 0.653, 2) for r in revenue_series]
        profit_series = [round(r * 0.347, 2) for r in revenue_series]
        
        return jsonify({
            'categories': categories,
            'revenue': revenue_series,
            'expense': expense_series,
            'profit': profit_series
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/ai-insights', methods=['GET'])
def get_ai_insights():
    try:
        region = request.args.get('region')
        month = request.args.get('month')
        segment = request.args.get('segment')
        product = request.args.get('product')
        period = request.args.get('period', 'yearly')

        q = get_filtered_query()
        rev_val = q.with_entities(func.sum(Order.amount)).scalar()
        revenue = float(rev_val) if rev_val is not None else 0.0
        sales = q.count()
        customers = q.with_entities(func.count(func.distinct(Order.name))).scalar() or 0

        delivered = q.filter(Order.status == 'Delivered').count()
        pending = q.filter(Order.status == 'Pending').count()
        processing = q.filter(Order.status == 'Processing').count()
        nps_total = sales
        nps = round(((delivered - pending) / nps_total) * 100, 1) if nps_total > 0 else 78.0

        def format_inr(val):
            val = round(val)
            s = str(val)
            if len(s) <= 3:
                return f"₹{s}"
            last3 = s[-3:]
            rest = s[:-3]
            groups = []
            while len(rest) > 2:
                groups.append(rest[-2:])
                rest = rest[:-2]
            if rest:
                groups.append(rest)
            groups.reverse()
            return f"₹{','.join(groups)},{last3}"

        margins = {
            'Apple iPhone 16': 0.28, 'Apple iPhone 16 Pro': 0.32,
            'Samsung Galaxy S25': 0.25, 'Samsung Galaxy S25 Ultra': 0.29,
            'OnePlus 14': 0.20, 'Google Pixel 10': 0.24,
            'MacBook Air M4': 0.35, 'MacBook Pro M4': 0.38,
            'Dell XPS 15': 0.32, 'HP Pavilion 15': 0.22,
            'Lenovo ThinkBook 16': 0.30, 'ASUS ROG Strix G16': 0.33,
            'iPad Air': 0.38, 'Samsung Galaxy Tab S10': 0.34,
            'Apple Watch Series 11': 0.40, 'Samsung Galaxy Watch 8': 0.35,
            'AirPods Pro 3': 0.45, 'Sony WH-1000XM6': 0.42,
            'JBL Flip 7': 0.30, 'Logitech MX Master 4': 0.50
        }
        orders_list = q.all()
        total_profit_amt = sum(float(o.amount) * margins.get(o.product, 0.347) for o in orders_list)
        profit_margin = round((total_profit_amt / revenue * 100), 1) if revenue > 0 else 34.7

        region_data = q.with_entities(Order.region, func.sum(Order.amount)).group_by(Order.region).all()
        top_region = max(region_data, key=lambda x: float(x[1]), default=('Maharashtra', 0))[0] if region_data else 'Maharashtra'
        top_region_rev = float(max(region_data, key=lambda x: float(x[1]), default=('', 0))[1]) if region_data else revenue * 0.45

        product_data = q.with_entities(Order.product, func.sum(Order.amount)).group_by(Order.product).all()
        top_product = max(product_data, key=lambda x: float(x[1]), default=('Apple iPhone 16', 0))[0] if product_data else 'Apple iPhone 16'
        top_product_rev = float(max(product_data, key=lambda x: float(x[1]), default=('', 0))[1]) if product_data else revenue * 0.40

        segment_data = q.with_entities(Order.segment, func.count(Order.id)).group_by(Order.segment).all()
        top_segment = max(segment_data, key=lambda x: x[1], default=('New Clients', 0))[0] if segment_data else 'New Clients'

        q_base = get_filtered_query(exclude_params=['period'])
        if not month or month in ('null', 'undefined'):
            curr_start, curr_end = get_period_bounds(period)
            prev_start, prev_end = get_previous_period_bounds(period)
            if prev_start and prev_end:
                prev_q = q_base.filter(func.str_to_date(Order.date, '%d/%m/%Y').between(prev_start, prev_end))
                prev_rev_val = prev_q.with_entities(func.sum(Order.amount)).scalar()
                prev_rev = float(prev_rev_val) if prev_rev_val else 0.0
            else:
                prev_rev = 0.0
            growth = round(((revenue - prev_rev) / prev_rev * 100), 1) if prev_rev > 0 else 18.3
        else:
            growth = 18.3

        next_period_rev = revenue * (1 + max(growth, 5.0) / 100)

        yearly_q = Order.query
        if region and region not in ('null', 'undefined'):
            yearly_q = yearly_q.filter(Order.region == region)
        if segment and segment not in ('null', 'undefined'):
            yearly_q = yearly_q.filter(Order.segment == segment)
        if product and product not in ('null', 'undefined'):
            yearly_q = yearly_q.filter(Order.product == product)

        monthly_revs = {}
        yearly_orders = yearly_q.all()
        month_names_map = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
                           7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
        for o in yearly_orders:
            try:
                m = int(o.date.split('/')[1])
                monthly_revs[m] = monthly_revs.get(m, 0.0) + float(o.amount)
            except:
                pass

        conf_categories = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        actual_vals = [round(monthly_revs.get(i+1, 0.0), 2) for i in range(12)]

        hist_total = sum(actual_vals[:6]) or 1
        avg_monthly = hist_total / 6
        forecast_vals = [None] * 6
        for i in range(6, 12):
            factor = 1 + (growth / 100) * ((i - 5) / 6)
            forecast_vals.append(round(avg_monthly * factor, 2))

        nonzero = [v for v in actual_vals[:6] if v > 0]
        if nonzero and len(nonzero) > 1:
            mean_rev = sum(nonzero) / len(nonzero)
            variance = sum((v - mean_rev) ** 2 for v in nonzero) / len(nonzero)
            std_dev = variance ** 0.5
            cv = (std_dev / mean_rev) * 100 if mean_rev > 0 else 50
            forecast_accuracy = round(max(60, min(98, 100 - cv * 0.4)), 1)
        else:
            forecast_accuracy = 92.4

        risk_score = round(min(100, (pending / max(sales, 1)) * 100 * 2 + len(Alert.query.all()) * 5), 0)
        risk_level = 'Low' if risk_score < 30 else ('Medium' if risk_score < 60 else 'High')
        upi_health = 'Optimal' if pending < 5 else ('Moderate' if pending < 15 else 'Degraded')

        max_rev = max(actual_vals[:6]) or 1
        sparkline_rev = [round((v / max_rev) * 100, 1) for v in actual_vals[:6]]
        sparkline_nps = [72, 74, 75, 76, 77, round(nps, 1)]
        sparkline_risk = [45, 40, 38, 35, 30, int(risk_score)]
        sparkline_growth = [10, 12, 14, 15, 17, round(max(growth, 5.0), 1)]

        top_region_pct = round((top_region_rev / revenue * 100), 1) if revenue > 0 else 45.0
        top_product_pct = round((top_product_rev / revenue * 100), 1) if revenue > 0 else 40.0

        insights = [
            {
                'type': 'revenue', 'title': 'Revenue Performance', 'icon': 'trending_up', 'color': '#4f46e5',
                'finding': f"{top_region} leads with {format_inr(top_region_rev)} ({top_region_pct}% of total). Revenue of {format_inr(revenue)} is trending {growth:.1f}% above prior period.",
                'confidence': min(97, round(forecast_accuracy)),
                'action': f'Scale enterprise contracts in {top_region} — highest ROI pipeline.',
                'supportingMetrics': {
                    'Total Revenue': format_inr(revenue), 'Top Region': top_region,
                    'Region Revenue': format_inr(top_region_rev), 'Region Share': f"{top_region_pct}%",
                    'Period Growth': f"{growth:.1f}%", 'Total Transactions': str(sales)
                }
            },
            {
                'type': 'customer', 'title': 'Customer Intelligence', 'icon': 'group', 'color': '#06b6d4',
                'finding': f"{customers} unique customers active. {top_segment} is the primary growth driver. NPS score of {round(nps)} reflects strong enterprise service quality.",
                'confidence': round(min(95, nps)),
                'action': 'Deploy targeted retention campaigns for Returning segment. Expand onboarding for New Clients.',
                'supportingMetrics': {
                    'Unique Customers': str(customers), 'NPS Score': str(round(nps)),
                    'Top Segment': top_segment, 'Delivered Orders': str(delivered), 'Pending Orders': str(pending)
                }
            },
            {
                'type': 'product', 'title': 'Product Analytics', 'icon': 'inventory_2', 'color': '#10b981',
                'finding': f"{top_product} is the highest-revenue product at {format_inr(top_product_rev)} ({top_product_pct}% share). Profit margin of {profit_margin:.1f}% exceeds SaaS industry benchmark.",
                'confidence': round(min(96, forecast_accuracy + 2)),
                'action': f'Prioritize {top_product} upsell campaigns. Bundle iPad Air with Apple iPhone 16.',
                'supportingMetrics': {
                    'Top Product': top_product, 'Product Revenue': format_inr(top_product_rev),
                    'Product Share': f"{top_product_pct}%", 'Profit Margin': f"{profit_margin:.1f}%", 'Active Orders': str(sales)
                }
            },
            {
                'type': 'risk', 'title': 'Risk & Compliance', 'icon': 'security', 'color': '#f59e0b',
                'finding': f"Business risk score: {int(risk_score)}/100 ({risk_level} Risk). {pending} pending transactions require review. UPI infrastructure: {upi_health}.",
                'confidence': round(min(90, 100 - risk_score * 0.5)),
                'action': 'Automate Razorpay retry workflows. Escalate pending orders older than 48 hours.',
                'supportingMetrics': {
                    'Risk Score': f"{int(risk_score)}/100", 'Risk Level': risk_level,
                    'Pending': str(pending), 'UPI Health': upi_health, 'Active Alerts': str(len(Alert.query.all()))
                }
            }
        ]

        recommendations = [
            {'priority': 'High', 'action': f'Increase digital marketing budget in {top_region} and adjacent tier-2 cities.', 'expectedImpact': f'+{min(25, round(growth + 5))}% revenue in next quarter'},
            {'priority': 'High', 'action': f'Accelerate {top_product} renewal pipeline — {processing} orders currently in processing.', 'expectedImpact': f'+{format_inr(processing * 200000)} additional MRR'},
            {'priority': 'Medium', 'action': 'Optimize UPI payment retry infrastructure to reduce transaction failures.', 'expectedImpact': 'Reduce payment failures by ~35%'}
        ]

        return jsonify({
            'kpis': {
                'forecastAccuracy': forecast_accuracy, 'revenuePrediction': max(growth, 5.0),
                'riskScore': int(risk_score), 'satisfactionScore': round(nps, 1), 'riskLevel': risk_level
            },
            'forecast': {
                'nextMonthRevenue': round(next_period_rev, 2), 'nextMonthRevenueFormatted': format_inr(next_period_rev),
                'predictedGrowth': max(growth, 5.0), 'confidenceAccuracy': forecast_accuracy,
                'actualSeries': actual_vals, 'forecastSeries': forecast_vals, 'categories': conf_categories,
                'explanation': f"Model trained on {len([v for v in actual_vals if v > 0])} months of data from {len(yearly_orders)} orders. Growth trajectory: {max(growth, 5.0):.1f}% period-over-period. Projected next-period revenue: {format_inr(next_period_rev)}."
            },
            'riskAnalysis': {
                'pendingOrders': pending, 'riskScore': int(risk_score), 'riskLevel': risk_level,
                'upiHealth': upi_health, 'alertCount': len(Alert.query.all())
            },
            'insights': insights,
            'predictive': {
                'topRegion': top_region, 'topRegionRevenue': format_inr(top_region_rev),
                'topProduct': top_product, 'topProductRevenue': format_inr(top_product_rev),
                'topSegment': top_segment, 'totalRevenue': format_inr(revenue),
                'profitMargin': profit_margin, 'trend': 'upward' if growth > 0 else 'downward'
            },
            'recommendations': recommendations,
            'sparklines': {
                'revenue': sparkline_rev, 'nps': sparkline_nps,
                'risk': sparkline_risk, 'growth': sparkline_growth
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/settings', methods=['GET'])
def get_settings():
    user = User.query.get(session.get('user_id'))
    if user:
        return jsonify({
            'username': user.username,
            'name': profile_settings.get('name', user.username),
            'email': profile_settings.get('email', ''),
            'role': user.role
        })
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/v1/settings', methods=['POST'])
def save_settings():
    global profile_settings
    try:
        data = request.json or {}
        if 'name' in data:
            profile_settings['name'] = data['name']
        if 'email' in data:
            profile_settings['email'] = data['email']
        return jsonify({'success': True, 'settings': profile_settings})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
