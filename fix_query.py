def fix_query():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    old_region = "if 'region' not in exclude_params and region and region != 'null' and region != 'undefined':"
    new_region = "if 'region' not in exclude_params and region and region not in ['null', 'undefined', 'all', 'All Products', 'All Status']:"
    content = content.replace(old_region, new_region)

    old_month = "if 'month' not in exclude_params and month and month != 'null' and month != 'undefined':"
    new_month = "if 'month' not in exclude_params and month and month not in ['null', 'undefined', 'all']:"
    content = content.replace(old_month, new_month)

    old_segment = "if 'segment' not in exclude_params and segment and segment != 'null' and segment != 'undefined':"
    new_segment = "if 'segment' not in exclude_params and segment and segment not in ['null', 'undefined', 'all']:"
    content = content.replace(old_segment, new_segment)

    old_product = "if 'product' not in exclude_params and product and product != 'null' and product != 'undefined':"
    new_product = "if 'product' not in exclude_params and product and product not in ['null', 'undefined', 'all', 'All Products']:"
    content = content.replace(old_product, new_product)

    # I'll also add a status check just in case get_filtered_query had it, although it doesn't look like it based on grep
    # Wait, get_orders also adds Order.status filter manually. So we are good.

    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("Fixed get_filtered_query successfully.")

if __name__ == '__main__':
    fix_query()
