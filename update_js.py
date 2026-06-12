with open('app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if '// --- API Gateway Simulator Event Bindings ---' in line:
        skip = True
    if skip and '});\n' == line and len(new_lines) > 0 and new_lines[-1] == '      });\n':
        # Let's just be careful with skipping. The easiest is using a substring replace.
        pass

# Actually, let's use string replace on the whole file content.
with open('app.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

# 1. Remove API simulator block
start_idx = js_content.find('// --- API Gateway Simulator Event Bindings ---')
end_idx = js_content.find('// --- Real-time 5-Second Auto-Refresh Loop ---')

if start_idx != -1 and end_idx != -1:
    js_content = js_content[:start_idx] + js_content[end_idx:]

# 2. Append renderExecutiveReports and bind export buttons
exec_reports_js = """
// --- Executive Reports Page ---
const renderExecutiveReports = () => {
  if (!currentAiData || !state.latestMetrics) return;

  const m = state.latestMetrics;
  const a = currentAiData;

  // Revenue Summary
  const revTotal = document.getElementById('exec-rev-total');
  const revMargin = document.getElementById('exec-rev-margin');
  const revNext = document.getElementById('exec-rev-next');
  const revGrowth = document.getElementById('exec-rev-growth');

  if (revTotal) revTotal.textContent = formatIndianRupees(m.revenue);
  if (revMargin) revMargin.textContent = m.profit.toFixed(1) + '%';
  if (revNext) revNext.textContent = a.forecast.nextMonthRevenueFormatted;
  if (revGrowth) {
    const growthSign = a.forecast.predictedGrowth >= 0 ? '+' : '';
    revGrowth.textContent = growthSign + a.forecast.predictedGrowth.toFixed(1) + '%';
    revGrowth.style.color = a.forecast.predictedGrowth >= 0 ? 'var(--success)' : 'var(--danger)';
  }

  // Sales Performance
  const salesTotal = document.getElementById('exec-sales-total');
  const salesProduct = document.getElementById('exec-sales-product');
  const salesProductRev = document.getElementById('exec-sales-product-rev');

  if (salesTotal) salesTotal.textContent = m.sales.toLocaleString('en-IN') + ' units';
  if (salesProduct) salesProduct.textContent = a.predictive.topProduct;
  if (salesProductRev) salesProductRev.textContent = a.predictive.topProductRevenue;

  // Customer Growth
  const custTotal = document.getElementById('exec-cust-total');
  const custSegment = document.getElementById('exec-cust-segment');
  const custNps = document.getElementById('exec-cust-nps');

  if (custTotal) custTotal.textContent = m.customers.toLocaleString('en-IN');
  if (custSegment) custSegment.textContent = a.predictive.topSegment;
  if (custNps) custNps.textContent = Math.round(a.kpis.satisfactionScore) + ' / 100';

  // Regional Performance
  const regTop = document.getElementById('exec-region-top');
  const regRev = document.getElementById('exec-region-rev');
  const regOrders = document.getElementById('exec-region-orders');

  if (regTop) regTop.textContent = a.predictive.topRegion;
  if (regRev) regRev.textContent = a.predictive.topRegionRevenue;
  if (regOrders) regOrders.textContent = m.orders.toLocaleString('en-IN') + ' orders';

  // AI Recommendations
  const recList = document.getElementById('exec-recommendations-list');
  if (recList && a.recommendations) {
    recList.innerHTML = a.recommendations.map(r => `<li><strong>${r.priority.toUpperCase()} Priority:</strong> ${r.action} — <em>${r.expectedImpact}</em></li>`).join('');
  }
};

// Bind Export Buttons on Executive Reports Page to trigger the main ones
setTimeout(() => {
  document.getElementById('execExportCSVBtn')?.addEventListener('click', () => {
    document.getElementById('exportCSVBtn')?.click();
  });
  document.getElementById('execDownloadPDFBtn')?.addEventListener('click', () => {
    document.getElementById('downloadReportBtn')?.click();
  });
}, 1000);

"""

# Insert it before the auto-refresh loop so it's in the main scope
loop_idx = js_content.find('// --- Real-time 5-Second Auto-Refresh Loop ---')
if loop_idx != -1:
    js_content = js_content[:loop_idx] + exec_reports_js + js_content[loop_idx:]

# 3. Add a call to renderExecutiveReports inside updateAiInsights
update_idx = js_content.find('renderAiRecommendations(data.recommendations);')
if update_idx != -1:
    insert_str = '\n      renderExecutiveReports();\n'
    # Insert after renderAiRecommendations
    insert_pos = update_idx + len('renderAiRecommendations(data.recommendations);')
    js_content = js_content[:insert_pos] + insert_str + js_content[insert_pos:]

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print("app.js updated.")
