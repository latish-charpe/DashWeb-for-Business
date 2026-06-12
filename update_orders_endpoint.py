import re

def update_orders_endpoint():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    new_get_orders = """@app.route('/api/v1/orders', methods=['GET'])
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
"""

    # We will just replace the entire get_orders() function.
    pattern = re.compile(r'@app\.route\(\'/api/v1/orders\', methods=\[\'GET\'\]\)\ndef get_orders\(\):.*?return jsonify\([^)]+\)\n    except Exception as e:\n        return jsonify\(\{\'error\': str\(e\)\}\), 500\n', re.DOTALL)
    
    if pattern.search(content):
        content = pattern.sub(new_get_orders + "\n", content)
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print('Successfully replaced get_orders() in app.py')
    else:
        print('Could not find pattern for get_orders()')

if __name__ == '__main__':
    update_orders_endpoint()
