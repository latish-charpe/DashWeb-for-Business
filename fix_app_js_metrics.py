with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Add the filter functions if not present
filter_funcs = """// --- Dynamic Dashboard Core Metrics Filtering ---
const filterByTopProduct = () => {
  const tpEl = document.getElementById('metric-top-product');
  if (tpEl && tpEl.textContent !== 'Loading...' && tpEl.textContent !== 'N/A') {
    state.filters.product = tpEl.textContent;
    updateDashboard();
    showToast(Filtered by Top Product: , 'success');
  }
};

const filterByStatus = (status) => {
  state.filters.status = status;
  updateDashboard();
  showToast(Filtered by Status: , 'success');
};
"""
if 'const filterByTopProduct' not in content:
    content += "\n" + filter_funcs

# In updateDashboard, after setting state.latestMetrics = metrics, update the new elements
old_update_nps = "      // Update NPS text elements immediately\n      const npsScoreEl = document.getElementById('npsScoreVal');"
new_update_nps = """      // Update new Dashboard Core Metrics
      const tpEl = document.getElementById('metric-top-product');
      const tpuEl = document.getElementById('metric-top-units');
      const aovEl = document.getElementById('metric-aov');
      const compEl = document.getElementById('metric-completed');
      const pendEl = document.getElementById('metric-pending');
      
      if (tpEl) tpEl.textContent = metrics.topProduct || 'N/A';
      if (tpuEl) tpuEl.textContent = ${(metrics.topProductUnits || 0).toLocaleString('en-IN')} units;
      if (aovEl) aovEl.textContent = formatIndianRupees(metrics.aov || 0);
      if (compEl) compEl.textContent = (metrics.completedOrders || 0).toLocaleString('en-IN');
      if (pendEl) pendEl.textContent = (metrics.pendingOrders || 0).toLocaleString('en-IN');

      // Update AI Health Score
      const healthCont = document.getElementById('health-score-container');
      const healthValEl = document.getElementById('dynamic-health-score');
      if (healthCont && healthValEl) {
        if (metrics.healthScore === null || metrics.healthScore === undefined) {
          healthCont.innerHTML = <span style="font-size: 1.2rem; color: var(--text-secondary);">Insufficient data for AI health analysis</span>;
          // Clear gauge if it exists
          const gauge = document.getElementById('healthGaugeContainer');
          if (gauge) gauge.innerHTML = '';
        } else {
          // Restore container if it was previously set to insufficient data
          if (!healthCont.querySelector('.score-max')) {
            healthCont.innerHTML = <span class="score-num"><span id="dynamic-health-score"></span><span class="score-max">/100</span></span>
                <p class="score-desc">Calculated based on Revenue Growth, Completed Order Percentage, Customer Growth, Profit Margin, and Pending Order Ratio.</p>;
          } else {
            document.getElementById('dynamic-health-score').textContent = metrics.healthScore;
          }
          
          // Draw a simple circular gauge using SVG if healthGaugeContainer is empty
          const gauge = document.getElementById('healthGaugeContainer');
          if (gauge) {
            let color = '#10b981'; // Green
            if (metrics.healthScore < 50) color = '#ef4444'; // Red
            else if (metrics.healthScore < 80) color = '#f59e0b'; // Yellow
            
            gauge.innerHTML = 
              <svg viewBox="0 0 36 36" style="width: 100%; height: 100%;">
                <path class="circle-bg"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none" stroke="#eee" stroke-width="3.8"/>
                <path class="circle"
                  stroke-dasharray=", 100"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none" stroke="" stroke-width="3.8" stroke-linecap="round"/>
              </svg>;
          }
        }
      }

      // Update NPS text elements immediately
      const npsScoreEl = document.getElementById('npsScoreVal');"""

content = content.replace(old_update_nps, new_update_nps)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated app.js successfully")
