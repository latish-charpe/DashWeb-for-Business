import re

def update_js():
    with open('app.js', 'r', encoding='utf-8') as f:
        content = f.read()

    js_code = """
  // --- Data Management Logic ---
  let ordersCurrentPage = 1;
  const ordersLimit = 10;
  
  const loadUploadHistory = async () => {
    try {
      const res = await fetch('/api/v1/data/history');
      if (res.ok) {
        const history = await res.json();
        const tbody = document.getElementById('uploadHistoryTableBody');
        if (tbody) {
          if (history.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align: center;">No uploads found.</td></tr>';
            return;
          }
          tbody.innerHTML = history.map(h => `
            <tr>
              <td>${h.file_name}</td>
              <td>${h.upload_date}</td>
              <td class="font-mono">${h.records_imported}</td>
              <td>${h.uploaded_by}</td>
            </tr>
          `).join('');
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  const loadDataOrders = async () => {
    try {
      const search = document.getElementById('orderSearch')?.value || '';
      const sort = document.getElementById('orderSort')?.value || 'date';
      const res = await fetch(`/api/v1/data/orders?page=${ordersCurrentPage}&limit=${ordersLimit}&search=${search}&sort_by=${sort}`);
      
      if (res.ok) {
        const result = await res.json();
        const tbody = document.getElementById('dataOrdersTableBody');
        if (tbody) {
          if (result.data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center;">No orders found.</td></tr>';
          } else {
            tbody.innerHTML = result.data.map(o => `
              <tr>
                <td class="font-mono text-muted">${o.id}</td>
                <td>${o.name}</td>
                <td>${o.product}</td>
                <td class="font-mono text-right">&#8377;${o.amount.toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
                <td>${o.region}</td>
                <td><span class="badge badge-${o.status === 'Delivered' ? 'success' : (o.status === 'Processing' ? 'primary' : 'warning')}">${o.status}</span></td>
                <td>${o.date}</td>
              </tr>
            `).join('');
          }
          
          document.getElementById('paginationInfo').textContent = `Showing page ${result.page} of ${result.pages || 1} (${result.total} orders)`;
          
          const prevBtn = document.getElementById('prevOrdersBtn');
          const nextBtn = document.getElementById('nextOrdersBtn');
          
          if (prevBtn) prevBtn.disabled = result.page <= 1;
          if (nextBtn) nextBtn.disabled = result.page >= result.pages;
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  // Add Order Form
  const addOrderForm = document.getElementById('addOrderForm');
  if (addOrderForm) {
    addOrderForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const payload = {
        name: document.getElementById('orderCustName').value,
        product: document.getElementById('orderProduct').value,
        amount: document.getElementById('orderAmount').value,
        region: document.getElementById('orderRegion').value,
        status: document.getElementById('orderStatus').value,
        date: document.getElementById('orderDate').value
      };
      
      try {
        const res = await fetch('/api/v1/orders/add', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          showToast('Order added successfully', 'success');
          addOrderForm.reset();
          loadDataOrders();
          updateDashboard(); // refresh KPIs
        } else {
          showToast('Failed to add order', 'error');
        }
      } catch (err) {
        showToast('Network error', 'error');
      }
    });
  }

  // CSV Upload
  const csvSelectBtn = document.getElementById('csvSelectBtn');
  const csvFileInput = document.getElementById('csvFileInput');
  if (csvSelectBtn && csvFileInput) {
    csvSelectBtn.addEventListener('click', () => csvFileInput.click());
    
    csvFileInput.addEventListener('change', async (e) => {
      if (e.target.files.length > 0) {
        const file = e.target.files[0];
        const formData = new FormData();
        formData.append('file', file);
        
        document.getElementById('csvUploadProgress').style.display = 'block';
        
        try {
          const res = await fetch('/api/v1/orders/upload', {
            method: 'POST',
            body: formData
          });
          const result = await res.json();
          document.getElementById('csvUploadProgress').style.display = 'none';
          
          if (res.ok) {
            showToast(`Imported ${result.successful} rows. Failed: ${result.failed}`, 'success');
            loadUploadHistory();
            loadDataOrders();
            updateDashboard(); // refresh KPIs
          } else {
            showToast(result.error || 'Upload failed', 'error');
          }
        } catch (err) {
          document.getElementById('csvUploadProgress').style.display = 'none';
          showToast('Upload failed due to network error', 'error');
        }
      }
    });
  }

  // Data Management Event Listeners
  document.getElementById('orderSearch')?.addEventListener('input', () => {
    ordersCurrentPage = 1;
    loadDataOrders();
  });
  document.getElementById('orderSort')?.addEventListener('change', () => {
    ordersCurrentPage = 1;
    loadDataOrders();
  });
  document.getElementById('prevOrdersBtn')?.addEventListener('click', () => {
    if (ordersCurrentPage > 1) {
      ordersCurrentPage--;
      loadDataOrders();
    }
  });
  document.getElementById('nextOrdersBtn')?.addEventListener('click', () => {
    ordersCurrentPage++;
    loadDataOrders();
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
    if "loadDataOrders()" not in content:
        content = content.replace("// --- Initializing App ---", f"{js_code}\n  // --- Initializing App ---")

    # Add view initialization for data-management
    view_init = """    if (viewId === 'data-management') {
      loadUploadHistory();
      loadDataOrders();
    }"""
    if "viewId === 'data-management'" not in content:
        content = content.replace("if (viewId === 'revenue') {", f"{view_init}\n    if (viewId === 'revenue') {{")

    with open('app.js', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    update_js()
