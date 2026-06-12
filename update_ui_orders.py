import re

def update_ui_orders():
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update the table-header-filters in #view-orders to include new filters
    old_filters = """          <div class="table-header-filters">
            <div class="search-bar border-style">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
              <input type="text" id="orderTableSearch" placeholder="Search orders..." />
            </div>
            <div class="filter-group">
              <select id="orderStatusFilter">
                <option value="all">All Status</option>
                <option value="Delivered">Delivered</option>
                <option value="Pending">Pending</option>
                <option value="Processing">Processing</option>
              </select>
            </div>
          </div>"""

    new_filters = """          <div class="table-header-filters" style="display: flex; flex-wrap: wrap; gap: 10px;">
            <div class="search-bar border-style">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
              <input type="text" id="orderTableSearch" placeholder="Search orders..." />
            </div>
            <div class="filter-group" style="display: flex; gap: 10px;">
              <select id="orderProductFilter" class="form-control" style="width: auto;">
                <option value="all">All Products</option>
                <option value="Core Cloud Suite">Core Cloud Suite</option>
                <option value="CRM Enterprise">CRM Enterprise</option>
                <option value="ThreatShield Guard">ThreatShield Guard</option>
                <option value="Integration Connect">Integration Connect</option>
              </select>
              <select id="orderStatusFilter" class="form-control" style="width: auto;">
                <option value="all">All Status</option>
                <option value="Delivered">Delivered</option>
                <option value="Pending">Pending</option>
                <option value="Processing">Processing</option>
              </select>
              <select id="orderSortFilter" class="form-control" style="width: auto;">
                <option value="date">Sort by Date</option>
                <option value="amount">Sort by Amount</option>
                <option value="name">Sort by Name</option>
              </select>
              <div style="display: flex; align-items: center; gap: 5px;">
                <input type="date" id="orderStartDate" class="form-control" style="width: 130px;"/>
                <span>to</span>
                <input type="date" id="orderEndDate" class="form-control" style="width: 130px;"/>
              </div>
            </div>
          </div>"""

    if old_filters in content:
        content = content.replace(old_filters, new_filters)
    elif "orderProductFilter" not in content:
        print("Could not find old filters to replace.")

    # 2. Add Pagination controls below the table in #view-orders
    old_table_end = """              </tbody>
            </table>
          </div>
        </div>
      </section>"""
      
    new_table_end = """              </tbody>
            </table>
            <div class="pagination" style="display: flex; justify-content: space-between; align-items: center; margin-top: 15px; padding: 10px 0;">
              <div class="pagination-info" id="mainOrdersPaginationInfo">Showing 0 orders</div>
              <div class="pagination-controls" style="display: flex; gap: 10px;">
                <button class="btn btn-secondary btn-sm" id="mainOrdersPrevBtn" disabled>Previous</button>
                <button class="btn btn-secondary btn-sm" id="mainOrdersNextBtn" disabled>Next</button>
              </div>
            </div>
          </div>
        </div>
      </section>"""
      
    if "mainOrdersPaginationInfo" not in content:
        content = content.replace(old_table_end, new_table_end)

    # 3. Move the Forms (Add New Order & CSV Dropzone) from #view-data-management to top of #view-orders
    # We will copy the data-mgmt-grid
    forms_html = """        <div class="data-mgmt-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 24px;">
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
            <div class="report-card-header" style="display: flex; justify-content: space-between; align-items: center;">
              <h3>Bulk CSV Upload</h3>
              <button class="btn btn-secondary btn-sm" id="downloadSampleBtn">Download Sample</button>
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
        </div>"""

    # Remove view-data-management section completely since we are merging it into view-orders
    if '<section class="dashboard-view" id="view-data-management">' in content:
        # Regex to remove the entire section. 
        # Using simple string splitting if possible
        parts = content.split('<section class="dashboard-view" id="view-data-management">')
        if len(parts) == 2:
            subparts = parts[1].split('</section>', 1)
            content = parts[0] + subparts[1]
            print("Removed #view-data-management")

    # Insert forms_html into #view-orders right after the view-header
    if 'id="addOrderForm"' not in content:
        view_orders_header_end = """            <p class="view-subtitle">Review, modify, filter, and track all incoming enterprise orders.</p>
          </div>
        </div>"""
        
        content = content.replace(view_orders_header_end, f"{view_orders_header_end}\n\n{forms_html}")

    # Remove Sidebar link for Data Management since we moved it to Orders Management
    sidebar_link = """        <li class="nav-item" data-view="data-management">
          <a href="#data-management" class="nav-link">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
            </svg>
            <span>Data Management</span>
          </a>
        </li>"""
    if sidebar_link in content:
        content = content.replace(sidebar_link + "\n", "")

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    update_ui_orders()
