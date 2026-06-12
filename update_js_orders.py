import re

def update_js_orders():
    with open('app.js', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update filterOrdersTable function
    old_filter_orders = """  const filterOrdersTable = async () => {
    const statusVal = statusFilter.value;
    const searchVal = searchInputTable.value;
    const queryStr = buildQueryString({ status: statusVal, search: searchVal });

    try {
      const orders = await fetch(`/api/v1/orders${queryStr}`).then(r => r.json());
      renderManagementTable(orders);
    } catch (e) {
      console.error("Error filtering orders table", e);
    }
  };"""

    new_filter_orders = """  const filterOrdersTable = async () => {
    const statusVal = document.getElementById('orderStatusFilter')?.value || 'all';
    const productVal = document.getElementById('orderProductFilter')?.value || 'all';
    const searchVal = document.getElementById('orderTableSearch')?.value || '';
    const sortVal = document.getElementById('orderSortFilter')?.value || 'date';
    const startVal = document.getElementById('orderStartDate')?.value || '';
    const endVal = document.getElementById('orderEndDate')?.value || '';
    
    let queryStr = `?page=${ordersCurrentPage}&limit=${ordersLimit}&search=${encodeURIComponent(searchVal)}&sort_by=${sortVal}&status=${statusVal}&product=${productVal}`;
    if (startVal && endVal) {
      queryStr += `&start_date=${startVal}&end_date=${endVal}`;
    }

    try {
      const result = await fetch(`/api/v1/orders${queryStr}`).then(r => r.json());
      if (result.data) {
        renderManagementTable(result.data);
        
        document.getElementById('mainOrdersPaginationInfo').textContent = `Showing page ${result.page} of ${result.pages || 1} (${result.total} orders)`;
        const prevBtn = document.getElementById('mainOrdersPrevBtn');
        const nextBtn = document.getElementById('mainOrdersNextBtn');
        if (prevBtn) prevBtn.disabled = result.page <= 1;
        if (nextBtn) nextBtn.disabled = result.page >= result.pages;
      } else {
        renderManagementTable(result); // Fallback if API doesn't have pagination structure yet
      }
    } catch (e) {
      console.error("Error filtering orders table", e);
    }
  };"""

    if old_filter_orders in content:
        content = content.replace(old_filter_orders, new_filter_orders)
    elif "filterOrdersTable = async () =>" in content:
        # regex replace
        pattern = re.compile(r'  const filterOrdersTable = async \(\) => \{.*?\n  \};', re.DOTALL)
        content = pattern.sub(new_filter_orders, content)
        
    # 2. Update event listeners in app.js
    # We remove loadDataOrders calls and add event listeners for the new UI
    
    # Let's just find where `document.getElementById('orderSearch')?.addEventListener` is and replace it
    pattern_event = re.compile(r'  // Data Management Event Listeners.*?document\.getElementById\(\'downloadSampleBtn\'\)\?\.addEventListener\(\'click\', \(\) => \{.*?\n  \}\);\n', re.DOTALL)
    
    new_event_listeners = """  // Orders Management Event Listeners
  document.getElementById('orderTableSearch')?.addEventListener('input', () => {
    ordersCurrentPage = 1;
    filterOrdersTable();
  });
  document.getElementById('orderStatusFilter')?.addEventListener('change', () => {
    ordersCurrentPage = 1;
    filterOrdersTable();
  });
  document.getElementById('orderProductFilter')?.addEventListener('change', () => {
    ordersCurrentPage = 1;
    filterOrdersTable();
  });
  document.getElementById('orderSortFilter')?.addEventListener('change', () => {
    ordersCurrentPage = 1;
    filterOrdersTable();
  });
  document.getElementById('orderStartDate')?.addEventListener('change', () => {
    ordersCurrentPage = 1;
    filterOrdersTable();
  });
  document.getElementById('orderEndDate')?.addEventListener('change', () => {
    ordersCurrentPage = 1;
    filterOrdersTable();
  });
  
  document.getElementById('mainOrdersPrevBtn')?.addEventListener('click', () => {
    if (ordersCurrentPage > 1) {
      ordersCurrentPage--;
      filterOrdersTable();
    }
  });
  document.getElementById('mainOrdersNextBtn')?.addEventListener('click', () => {
    ordersCurrentPage++;
    filterOrdersTable();
  });

  document.getElementById('downloadSampleBtn')?.addEventListener('click', () => {
    const csvContent = "Customer Name,Product,Amount,Region,Status,Date\\nJohn Doe,Core Cloud Suite,150000.00,Maharashtra,Delivered,15/08/2026\\nJane Smith,CRM Enterprise,250000.00,Karnataka,Processing,16/08/2026";
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", "Sample_Orders_Upload.csv");
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  });
"""
    if pattern_event.search(content):
        content = pattern_event.sub(new_event_listeners, content)
        
    # Replace calls to loadDataOrders() with filterOrdersTable() in AddOrderForm and CSV upload logic
    content = content.replace("loadDataOrders();", "filterOrdersTable();")

    # The original event listeners for searchInputTable and statusFilter might still exist, let's remove them
    old_listeners = """  searchInputTable.addEventListener('input', debounce(filterOrdersTable, 300));
  statusFilter.addEventListener('change', filterOrdersTable);"""
    if old_listeners in content:
        content = content.replace(old_listeners, "")
        
    # Fix the table body id if renderManagementTable hardcodes it
    # No, renderManagementTable uses 'ordersManagementTableBody'
    
    with open('app.js', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    update_js_orders()
