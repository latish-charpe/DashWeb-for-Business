with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re

# Replace Indian Business Metrics
old_indian_metrics = re.search(r"          <!-- Indian Business Metrics -->\n          <div class=\"widget-card indian-metrics-card\">.*?</div>\n          </div>", content, flags=re.DOTALL)
if not old_indian_metrics:
    print("Could not find Indian Business Metrics block")
    exit(1)

new_metrics_html = """          <!-- Dynamic Database Metrics -->
          <div class="widget-card indian-metrics-card" style="padding-bottom: 20px;">
            <div class="widget-header">
              <h3>Core Operations Metrics</h3>
              <span class="widget-subtitle">Click cards to filter dashboard</span>
            </div>
            <div class="indian-metrics-grid" style="gap: 15px;">
              <div class="metric-item-box clickable-metric" onclick="filterByTopProduct()" style="cursor: pointer; transition: transform 0.2s;">
                <span class="m-box-title">Top Selling Product</span>
                <span class="m-box-val" id="metric-top-product" style="font-size: 1.2rem;">Loading...</span>
                <span class="m-box-sub text-success" id="metric-top-units">... units</span>
              </div>
              <div class="metric-item-box">
                <span class="m-box-title">Average Order Value (AOV)</span>
                <span class="m-box-val" id="metric-aov">Loading...</span>
                <span class="m-box-sub text-success">Per transaction</span>
              </div>
              <div class="metric-item-box clickable-metric" onclick="filterByStatus('Delivered')" style="cursor: pointer; transition: transform 0.2s;">
                <span class="m-box-title">Completed Orders</span>
                <span class="m-box-val" id="metric-completed">Loading...</span>
                <span class="m-box-sub text-success">Fully Delivered</span>
              </div>
              <div class="metric-item-box clickable-metric" onclick="filterByStatus('Pending')" style="cursor: pointer; transition: transform 0.2s;">
                <span class="m-box-title">Pending Orders</span>
                <span class="m-box-val" id="metric-pending">Loading...</span>
                <span class="m-box-sub" style="color: #f59e0b;">Awaiting processing</span>
              </div>
            </div>
          </div>"""

content = content.replace(old_indian_metrics.group(0), new_metrics_html)

# Update Health Score
old_health_meta = """              <div class="health-score-meta">
                <span class="score-num">92<span class="score-max">/100</span></span>
                <p class="score-desc">Calculated across 14 financial and performance pipeline indicators. 0% critical transaction latency.</p>
              </div>"""
new_health_meta = """              <div class="health-score-meta" id="health-score-container">
                <span class="score-num"><span id="dynamic-health-score">...</span><span class="score-max">/100</span></span>
                <p class="score-desc">Calculated based on Revenue Growth, Completed Order Percentage, Customer Growth, Profit Margin, and Pending Order Ratio.</p>
              </div>"""

content = content.replace(old_health_meta, new_health_meta)

# Update cache
content = content.replace('app.js?v=3.7.0', 'app.js?v=3.8.0')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated index.html successfully")
