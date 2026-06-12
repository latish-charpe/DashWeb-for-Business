with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace Nav item
old_nav = '''        <li class="nav-item" data-view="api-simulator">
          <a href="#api-simulator" class="nav-link">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="16 18 22 12 16 6"/>
              <polyline points="8 6 2 12 8 18"/>
            </svg>
            <span>API Simulator</span>
            <span class="badge badge-primary" style="background: var(--success-glow); color: var(--success);">Live</span>
          </a>
        </li>'''

new_nav = '''        <li class="nav-item" data-view="executive-reports">
          <a href="#executive-reports" class="nav-link">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10 9 9 9 8 9"/>
            </svg>
            <span>Executive Reports</span>
          </a>
        </li>'''

html = html.replace(old_nav, new_nav)

# Replace View section
start_view = html.find('<!-- VIEW 9: API SIMULATOR -->')
end_view = html.find('    </main>')

if start_view != -1 and end_view != -1:
    new_view = '''      <!-- VIEW 9: EXECUTIVE REPORTS -->
      <section class="dashboard-view" id="view-executive-reports">
        <div class="view-header">
          <div>
            <span class="breadcrumb">Management &gt; Executive Reports</span>
            <h1 class="view-title">Executive Summary & Business Reports</h1>
            <p class="view-subtitle">Comprehensive business summaries and strategic insights.</p>
          </div>
          <div class="view-actions">
            <button class="btn btn-secondary" id="execExportCSVBtn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/>
              </svg>
              <span>Export CSV (&#8377;)</span>
            </button>
            <button class="btn btn-primary" id="execDownloadPDFBtn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>
              </svg>
              <span>Export PDF Report</span>
            </button>
          </div>
        </div>

        <div class="executive-report-grid">
          
          <!-- Revenue Summary -->
          <div class="report-card">
            <div class="report-card-header">
              <h3>Revenue Summary</h3>
            </div>
            <div class="report-card-body">
              <table class="data-table">
                <tbody>
                  <tr>
                    <td>Total Portfolio Revenue</td>
                    <td id="exec-rev-total" class="font-mono strong text-right">--</td>
                  </tr>
                  <tr>
                    <td>Profit Margin</td>
                    <td id="exec-rev-margin" class="font-mono text-right">--</td>
                  </tr>
                  <tr>
                    <td>Projected Next Period</td>
                    <td id="exec-rev-next" class="font-mono text-right">--</td>
                  </tr>
                  <tr>
                    <td>Expected Growth</td>
                    <td id="exec-rev-growth" class="font-mono text-right">--</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Sales Performance Report -->
          <div class="report-card">
            <div class="report-card-header">
              <h3>Sales Performance Report</h3>
            </div>
            <div class="report-card-body">
              <table class="data-table">
                <tbody>
                  <tr>
                    <td>Total Sales</td>
                    <td id="exec-sales-total" class="font-mono strong text-right">--</td>
                  </tr>
                  <tr>
                    <td>Top Performing Product</td>
                    <td id="exec-sales-product" class="text-right">--</td>
                  </tr>
                  <tr>
                    <td>Product Revenue</td>
                    <td id="exec-sales-product-rev" class="font-mono text-right">--</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Customer Growth Report -->
          <div class="report-card">
            <div class="report-card-header">
              <h3>Customer Growth Report</h3>
            </div>
            <div class="report-card-body">
              <table class="data-table">
                <tbody>
                  <tr>
                    <td>Total Customers</td>
                    <td id="exec-cust-total" class="font-mono strong text-right">--</td>
                  </tr>
                  <tr>
                    <td>Fastest Growing Segment</td>
                    <td id="exec-cust-segment" class="text-right">--</td>
                  </tr>
                  <tr>
                    <td>Customer Satisfaction (NPS)</td>
                    <td id="exec-cust-nps" class="font-mono text-right">--</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Regional Performance Report -->
          <div class="report-card">
            <div class="report-card-header">
              <h3>Regional Performance Report</h3>
            </div>
            <div class="report-card-body">
              <table class="data-table">
                <tbody>
                  <tr>
                    <td>Top Growth Region</td>
                    <td id="exec-region-top" class="text-right">--</td>
                  </tr>
                  <tr>
                    <td>Region Revenue</td>
                    <td id="exec-region-rev" class="font-mono text-right">--</td>
                  </tr>
                  <tr>
                    <td>Total Orders</td>
                    <td id="exec-region-orders" class="font-mono text-right">--</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- AI Business Recommendations -->
          <div class="report-card" style="grid-column: 1 / -1;">
            <div class="report-card-header">
              <h3>AI Business Recommendations</h3>
            </div>
            <div class="report-card-body">
              <ul class="exec-recommendations-list" id="exec-recommendations-list">
                <!-- Populated by JS -->
                <li>Loading recommendations...</li>
              </ul>
            </div>
          </div>

        </div>
      </section>\n\n'''
    html = html[:start_view] + new_view + html[end_view:]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html updated.")
