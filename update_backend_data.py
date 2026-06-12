import re

def update_backend():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Add imports
    imports = "import csv\nimport io\nimport uuid\nfrom datetime import datetime\n"
    if "import csv" not in content:
        content = imports + content

    # Add UploadHistory model
    if "class UploadHistory(" not in content:
        upload_history_model = """
class UploadHistory(db.Model):
    __tablename__ = 'upload_history'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    file_name = db.Column(db.String(200), nullable=False)
    upload_date = db.Column(db.String(50), nullable=False)
    records_imported = db.Column(db.Integer, nullable=False)
    uploaded_by = db.Column(db.String(100), nullable=False)
"""
        content = content.replace("class Alert(db.Model):", f"{upload_history_model}\nclass Alert(db.Model):")

    # Ensure UploadHistory table is created
    if "db.create_all()" in content and "UploadHistory" not in content.split("db.create_all()")[1][:50]:
        # db.create_all() will handle the new model automatically
        pass

    # Add Endpoints
    endpoints = """
@app.route('/api/v1/orders/add', methods=['POST'])
def add_order():
    try:
        data = request.json
        amount = float(data.get('amount', 0))
        date_str = data.get('date') # Expected DD/MM/YYYY
        
        # Calculate month from date
        try:
            dt = datetime.strptime(date_str, '%d/%m/%Y')
            month = dt.strftime('%b') # 'Jul', 'Aug', etc.
        except:
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
                    dt = datetime.strptime(date_str, '%d/%m/%Y')
                    month = dt.strftime('%b')
                except:
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
            upload_date=datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
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
"""
    if "/api/v1/orders/upload" not in content:
        content = content.replace("# --- API Endpoints ---", f"# --- API Endpoints ---\n{endpoints}")

    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    update_backend()
