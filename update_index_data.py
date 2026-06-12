import re

def update_index():
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add Sidebar Link
    sidebar_link = """        <li class="nav-item" data-view="data-management">
          <a href="#data-management" class="nav-link">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
            </svg>
            <span>Data Management</span>
          </a>
        </li>
"""
    if 'data-view="data-management"' not in content:
        content = content.replace('<div class="nav-section">PREFERENCES</div>', f"{sidebar_link}\n      <div class=\"nav-section\">PREFERENCES</div>")

    # 2. Add Data Management Section
    data_mgmt_html = """
      <!-- VIEW 10: DATA MANAGEMENT -->
      <section class="dashboard-view" id="view-data-management">
        <div class="view-header">
          <div>
            <span class="breadcrumb">Management &gt; Data Management</span>
            <h1 class="view-title">Data Source & Uploads</h1>
            <p class="view-subtitle">Manually insert new records or bulk upload CSV data to update dashboard KPIs.</p>
          </div>
          <div class="view-actions">
            <button class="btn btn-secondary" id="downloadSampleBtn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/>
              </svg>
              <span>Download Sample CSV</span>
            </button>
          </div>
        </div>

        <div class="data-mgmt-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 24px;">
          <!-- Add New Order Form -->
          <div class="report-card">
            <div class="report-card-header">
              <h3>Add New Order</h3>
            </div>
            <div class="report-card-body">
              <form id="addOrderForm">
                <div class="form-group" style="margin-bottom: 15px;">
                  <label>Customer Name</label>
                  <input type="text" class="form-control" id="orderCustName" required />
                </div>
                <div class="form-group" style="margin-bottom: 15px;">
                  <label>Product</label>
                  <select class="form-control" id="orderProduct" required>
                    <option value="Core Cloud Suite">Core Cloud Suite</option>
                    <option value="CRM Enterprise">CRM Enterprise</option>
                    <option value="ThreatShield Guard">ThreatShield Guard</option>
                    <option value="Integration Connect">Integration Connect</option>
                  </select>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                  <div class="form-group">
                    <label>Amount (₹)</label>
                    <input type="number" step="0.01" class="form-control" id="orderAmount" required />
                  </div>
                  <div class="form-group">
                    <label>Date (DD/MM/YYYY)</label>
                    <input type="text" class="form-control" id="orderDate" placeholder="e.g. 15/08/2026" required />
                  </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
                  <div class="form-group">
                    <label>Region</label>
                    <select class="form-control" id="orderRegion" required>
                      <option value="Maharashtra">Maharashtra</option>
                      <option value="Karnataka">Karnataka</option>
                      <option value="Delhi">Delhi</option>
                      <option value="Gujarat">Gujarat</option>
                      <option value="Tamil Nadu">Tamil Nadu</option>
                    </select>
                  </div>
                  <div class="form-group">
                    <label>Status</label>
                    <select class="form-control" id="orderStatus" required>
                      <option value="Delivered">Delivered</option>
                      <option value="Processing">Processing</option>
                      <option value="Pending">Pending</option>
                    </select>
                  </div>
                </div>
                <button type="submit" class="btn btn-primary" style="width: 100%;">Save Order</button>
              </form>
            </div>
          </div>

          <!-- CSV Upload -->
          <div class="report-card">
            <div class="report-card-header">
              <h3>Bulk CSV Upload</h3>
            </div>
            <div class="report-card-body" style="display: flex; flex-direction: column; justify-content: center;">
              <div class="csv-dropzone" id="csvDropzone">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-bottom: 15px; color: var(--text-muted);">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
                </svg>
                <p>Drag and drop your .csv file here</p>
                <p class="text-muted" style="font-size: 12px; margin-top: 5px;">or</p>
                <button class="btn btn-secondary" style="margin-top: 10px;" id="csvSelectBtn">Browse Files</button>
                <input type="file" id="csvFileInput" accept=".csv" style="display: none;" />
              </div>
              <div id="csvUploadProgress" style="display: none; margin-top: 15px;">
                <p>Uploading and processing...</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Upload History -->
        <div class="report-card" style="margin-bottom: 24px;">
          <div class="report-card-header">
            <h3>Recent Upload History</h3>
          </div>
          <div class="report-card-body">
            <table class="data-table">
              <thead>
                <tr>
                  <th>File Name</th>
                  <th>Upload Date</th>
                  <th>Records Imported</th>
                  <th>Uploaded By</th>
                </tr>
              </thead>
              <tbody id="uploadHistoryTableBody">
                <tr><td colspan="4" style="text-align: center;">Loading history...</td></tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- View Orders -->
        <div class="report-card">
          <div class="report-card-header" style="display: flex; justify-content: space-between; align-items: center;">
            <h3>View Orders</h3>
            <div class="table-toolbar" style="display: flex; gap: 10px;">
              <input type="text" class="form-control" id="orderSearch" placeholder="Search orders..." style="padding: 6px 12px; width: 200px;" />
              <select class="form-control" id="orderSort" style="padding: 6px 12px; width: 150px;">
                <option value="date">Sort by Date</option>
                <option value="amount">Sort by Amount</option>
                <option value="name">Sort by Name</option>
              </select>
            </div>
          </div>
          <div class="report-card-body" style="overflow-x: auto;">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Order ID</th>
                  <th>Customer Name</th>
                  <th>Product</th>
                  <th style="text-align: right;">Amount (₹)</th>
                  <th>Region</th>
                  <th>Status</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody id="dataOrdersTableBody">
                <tr><td colspan="7" style="text-align: center;">Loading orders...</td></tr>
              </tbody>
            </table>
            <div class="pagination" style="display: flex; justify-content: space-between; align-items: center; margin-top: 15px;">
              <div class="pagination-info" id="paginationInfo">Showing 0 orders</div>
              <div class="pagination-controls" style="display: flex; gap: 10px;">
                <button class="btn btn-secondary btn-sm" id="prevOrdersBtn" disabled>Previous</button>
                <button class="btn btn-secondary btn-sm" id="nextOrdersBtn" disabled>Next</button>
              </div>
            </div>
          </div>
        </div>

      </section>
"""
    if 'id="view-data-management"' not in content:
        content = content.replace("</main>", f"{data_mgmt_html}\n    </main>")

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    update_index()
