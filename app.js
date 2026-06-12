// --- InsightHub - Advanced Business Intelligence Engine ---


// --- Global Fetch Interceptor for Auth ---
const originalFetch = window.fetch;
window.fetch = async function() {
    const response = await originalFetch.apply(this, arguments);
    if (response.status === 401) {
        window.location.href = '/login?expired=1';
    }
    return response;
};

document.addEventListener('DOMContentLoaded', () => {
  let ordersCurrentPage = 1;
  const ordersLimit = 10;

  // --- State Variables ---
  let currentTheme = 'light';
  let chartInstances = {};
  
  // Central Filters & Drill-down State
  const state = {
    filters: {
      region: null,       // 'Maharashtra', 'Gujarat', 'Karnataka', 'Telangana', 'Delhi'
      period: 'monthly',   // 'daily', 'weekly', 'monthly', 'quarterly', 'yearly'
      month: null,        // 'Jul', 'Aug', 'Sep', etc.
      segment: null,      // 'New Clients', 'Returning'
      product: null       // 'Apple iPhone 16', 'Samsung Galaxy S25', etc.
    },
    drillLevel: 'dashboard',
    latestMetrics: {
      revenue: 48256000,
      sales: 138,
      customers: 90,
      orders: 138,
      profit: 34.7,
      growth: 18.3
    }
  };

  // --- Indian Rupee Formatter ---
  const formatIndianRupees = (value) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(value);
  };

  // Build query string based on current state filters
  const buildQueryString = (additionalParams = {}) => {
    const params = new URLSearchParams();
    if (state.filters.region) params.append('region', state.filters.region);
    if (state.filters.month) params.append('month', state.filters.month);
    if (state.filters.segment) params.append('segment', state.filters.segment);
    if (state.filters.product) params.append('product', state.filters.product);
    if (state.filters.period) params.append('period', state.filters.period);
    
    for (const [k, v] of Object.entries(additionalParams)) {
      if (v !== undefined && v !== null) {
        params.append(k, v);
      }
    }
    return params.toString() ? '?' + params.toString() : '';
  };

  // --- Element Selectors ---
  const liveClockEl = document.getElementById('liveClock');
  const themeToggleBtn = document.getElementById('themeToggle');
  const sidebarToggleBtn = document.getElementById('sidebarToggle');
  const mobileToggleBtn = document.getElementById('mobileToggle');
  const sidebar = document.getElementById('sidebar');
  const contentWrapper = document.getElementById('contentWrapper');
  const notifBell = document.getElementById('notifBell');
  const notifDropdown = document.getElementById('notifDropdown');
  const clearAllNotifBtn = document.getElementById('clearAllNotifications');
  const dropdownNotifList = document.getElementById('dropdownNotifList');
  const profileTrigger = document.getElementById('profileTrigger');
  const profileDropdown = document.getElementById('profileDropdown');
  const navItems = document.querySelectorAll('.sidebar-nav .nav-item');
  const viewSwitchTriggers = document.querySelectorAll('.view-switch-trigger');
  const views = document.querySelectorAll('.dashboard-view');
  
  // Dashboard Metrics
  const kpiRev = document.getElementById('kpiVal-revenue');
  const kpiSales = document.getElementById('kpiVal-sales');
  const kpiCust = document.getElementById('kpiVal-customers');
  const kpiOrd = document.getElementById('kpiVal-orders');
  const kpiProf = document.getElementById('kpiVal-profit');
  const kpiGrow = document.getElementById('kpiVal-growth');

  // KPI Card Routing Click Listeners
  const cardsRouting = [
    { id: 'kpi-revenue', view: 'revenue' },
    { id: 'kpi-sales', view: 'sales' },
    { id: 'kpi-customers', view: 'customers' },
    { id: 'kpi-orders', view: 'orders' },
    { id: 'kpi-profit', view: 'revenue' },
    { id: 'kpi-growth', view: 'ai-insights' }
  ];
  cardsRouting.forEach(card => {
    const el = document.getElementById(card.id);
    if (el) {
      el.addEventListener('click', () => {
        switchView(card.view);
        showToast(`Navigated to ${card.view.replace('-', ' ')} view from KPI card click.`, 'success');
      });
    }
  });

  // --- Toast & UI Helpers ---
  const showToast = (message, type = 'info') => {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.innerHTML = `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>
      </svg>
      <span>${message}</span>
    `;
    toast.style.borderColor = type === 'success' ? 'var(--success)' : 'var(--primary)';
    toast.classList.add('active');
    setTimeout(() => {
      toast.classList.remove('active');
    }, 3500);
  };

  // Live Clock
  const updateClock = () => {
    if (!liveClockEl) return;
    const now = new Date();
    let hours = now.getHours();
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12; 
    const hoursStr = String(hours).padStart(2, '0');
    liveClockEl.textContent = `${hoursStr}:${minutes}:${seconds} ${ampm}`;
  };
  setInterval(updateClock, 1000);
  updateClock();

  // Theme Toggler
  const setTheme = (theme) => {
    document.documentElement.setAttribute('data-theme', theme);
    currentTheme = theme;
    
    const sunIcon = themeToggleBtn.querySelector('.sun-icon');
    const moonIcon = themeToggleBtn.querySelector('.moon-icon');
    if (theme === 'light') {
      if (sunIcon) sunIcon.style.display = 'none';
      if (moonIcon) moonIcon.style.display = 'block';
    } else {
      if (sunIcon) sunIcon.style.display = 'block';
      if (moonIcon) moonIcon.style.display = 'none';
    }
    
    renderAllCharts();
  };

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', () => {
      const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
      setTheme(nextTheme);
      showToast(`App theme switched to ${nextTheme} mode.`, 'success');
    });
  }

  // --- Modal Controllers ---
  const globalModal = document.getElementById('globalModal');
  const modalTitle = document.getElementById('modalTitle');
  const modalBody = document.getElementById('modalBody');
  const modalCloseBtn = document.getElementById('modalCloseBtn');

  const openModal = (title, htmlContent) => {
    if (!globalModal) return;
    modalTitle.textContent = title;
    modalBody.innerHTML = htmlContent;
    globalModal.classList.add('active');
  };

  const closeModal = () => {
    if (!globalModal) return;
    globalModal.classList.remove('active');
  };

  if (modalCloseBtn) modalCloseBtn.addEventListener('click', closeModal);
  if (globalModal) {
    globalModal.addEventListener('click', (e) => {
      if (e.target === globalModal) closeModal();
    });
  }

  // --- Modal Invoices ---
  const openOrderDetailsModal = (order) => {
    const statusClass = order.status === 'Delivered' ? 'status-delivered' : (order.status === 'Pending' ? 'status-pending' : 'status-processing');
    const billingDetailsHtml = `
      <div style="font-family: var(--font-family); line-height: 1.6;">
        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--sidebar-border); padding-bottom: 12px; margin-bottom: 16px;">
          <div>
            <span style="font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase;">Transaction Invoice</span>
            <h4 style="margin-top: 4px; font-weight: 800; font-size: 1.15rem;">${order.id}</h4>
          </div>
          <div style="text-align: right;">
            <span class="badge-status ${statusClass}" style="margin-top: 4px;">${order.status}</span>
          </div>
        </div>
        
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
          <tr>
            <td style="padding: 6px 0; color: var(--text-secondary); font-weight: 600;">Customer Name:</td>
            <td style="padding: 6px 0; font-weight: 700; text-align: right;">${order.name}</td>
          </tr>
          <tr>
            <td style="padding: 6px 0; color: var(--text-secondary); font-weight: 600;">Product SKU:</td>
            <td style="padding: 6px 0; font-weight: 700; text-align: right; color: var(--primary);">${order.product}</td>
          </tr>
          <tr>
            <td style="padding: 6px 0; color: var(--text-secondary); font-weight: 600;">Transaction Date:</td>
            <td style="padding: 6px 0; font-weight: 700; text-align: right;">${order.date}</td>
          </tr>
          <tr>
            <td style="padding: 6px 0; color: var(--text-secondary); font-weight: 600;">Payment Protocol:</td>
            <td style="padding: 6px 0; font-weight: 700; text-align: right; color: var(--secondary);">Razorpay UPI API v2</td>
          </tr>
          <tr>
            <td style="padding: 6px 0; color: var(--text-secondary); font-weight: 600;">Gateway Latency:</td>
            <td style="padding: 6px 0; font-weight: 700; text-align: right; color: var(--success);">142ms (Healthy)</td>
          </tr>
        </table>
        
        <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid var(--panel-border); padding: 16px; border-radius: 12px; margin-bottom: 20px;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-weight: 700; color: var(--text-secondary);">Total Billable Amount:</span>
            <span style="font-size: 1.35rem; font-weight: 800; color: var(--text-primary);">${formatIndianRupees(order.amount)}</span>
          </div>
        </div>

        <div style="display: flex; gap: 12px; justify-content: flex-end;">
          <button class="btn btn-secondary" onclick="document.getElementById('modalCloseBtn').click()">Close Invoice</button>
          <button class="btn btn-primary" onclick="showToast('Invoice ${order.id} sent to print queue.', 'success'); document.getElementById('modalCloseBtn').click()">Print Receipt</button>
        </div>
      </div>
    `;
    openModal('Enterprise Invoice Details', billingDetailsHtml);
  };

  // --- Modal Alerts ---
  const openAlertDetailsModal = (alert) => {
    let statusLabel = 'Critical';
    if (alert.type === 'warning') statusLabel = 'Pending Review';
    if (alert.type === 'info') statusLabel = 'Monitor Info';
    if (alert.type === 'success') statusLabel = 'Resolved';
    if (alert.type === 'danger') statusLabel = 'Escalated / Critical';
    
    const alertDetailsHtml = `
      <div style="font-family: var(--font-family); line-height: 1.6;">
        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--sidebar-border); padding-bottom: 12px; margin-bottom: 16px;">
          <div>
            <span style="font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase;">System Incident Alert</span>
            <h4 style="margin-top: 4px; font-weight: 800; font-size: 1.15rem;">${alert.title}</h4>
          </div>
          <div>
            <span class="badge-status status-${alert.type === 'info' ? 'processing' : alert.type}" id="modalAlertStatusBadge" style="margin-top: 4px;">${statusLabel}</span>
          </div>
        </div>
        
        <p style="color: var(--text-secondary); margin-bottom: 20px; font-size: 0.95rem;">
          ${alert.desc}
        </p>

        <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid var(--panel-border); padding: 14px; border-radius: 12px; margin-bottom: 20px;">
          <h4 style="font-weight: 700; font-size: 0.85rem; text-transform: uppercase; color: var(--text-muted); margin-bottom: 8px;">Incident Log Metrics:</h4>
          <ul style="list-style: none; padding-left: 0; font-size: 0.82rem; color: var(--text-secondary); display: flex; flex-direction: column; gap: 6px;">
            <li>&bull; <strong>Trigger Source:</strong> Node-${alert.tag.replace(' ', '-').toLowerCase()}</li>
            <li>&bull; <strong>Reported Latency:</strong> 240ms (exceeds SLA threshold of 150ms)</li>
            <li>&bull; <strong>System Health Impact:</strong> Degradation factor 4.8%</li>
          </ul>
        </div>

        <div style="display: flex; gap: 8px; justify-content: flex-end; flex-wrap: wrap;">
          <button class="btn btn-secondary" onclick="document.getElementById('modalCloseBtn').click()">Close</button>
          <button class="btn" id="btnPendingAlert" style="background: var(--warning-glow); color: var(--warning); border: 1px solid var(--warning);">Mark Pending</button>
          <button class="btn" id="btnEscalateAlert" style="background: var(--danger-glow); color: var(--danger); border: 1px solid var(--danger);">Escalate</button>
          <button class="btn btn-primary" id="btnResolveAlert" style="background: var(--success); color: #fff;">Mark Resolved</button>
        </div>
      </div>
    `;
    openModal('Incident Details Monitor', alertDetailsHtml);

    // Add click handlers
    setTimeout(() => {
      const resolveBtn = document.getElementById('btnResolveAlert');
      const pendingBtn = document.getElementById('btnPendingAlert');
      const escalateBtn = document.getElementById('btnEscalateAlert');

      const triggerAlertUpdate = async (updatedFields) => {
        try {
          const res = await fetch(`/api/v1/alerts/${alert.id}/status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updatedFields)
          }).then(r => r.json());
          
          if (res.success) {
            updateDashboard();
            document.getElementById('modalCloseBtn').click();
          }
        } catch (e) {
          showToast('Failed to update alert in database', 'danger');
        }
      };

      if (resolveBtn) {
        resolveBtn.addEventListener('click', () => {
          triggerAlertUpdate({
            type: 'success',
            title: alert.title.replace('⚠️', '✅').replace('📈', '✅').replace('💳', '✅'),
            desc: 'Incident has been resolved by CEO Shrikant Keche.'
          });
          showToast('Incident marked as RESOLVED.', 'success');
        });
      }

      if (pendingBtn) {
        pendingBtn.addEventListener('click', () => {
          triggerAlertUpdate({ type: 'warning' });
          showToast('Incident status changed to PENDING REVIEW.', 'info');
        });
      }

      if (escalateBtn) {
        escalateBtn.addEventListener('click', () => {
          triggerAlertUpdate({ type: 'danger' });
          showToast('Incident has been ESCALATED to level 2 support.', 'danger');
        });
      }
    }, 100);
  };

  // --- Dynamic Timeline Event Modal ---
  const openTimelineDetailsModal = (evt) => {
    const detailsHtml = `
      <div style="font-family: var(--font-family); line-height: 1.6;">
        <div style="border-bottom: 1px solid var(--sidebar-border); padding-bottom: 12px; margin-bottom: 16px;">
          <span style="font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase;">Audit Log Event</span>
          <h4 style="margin-top: 4px; font-weight: 800; font-size: 1.15rem;">${evt.title}</h4>
          <span style="font-size: 0.82rem; color: var(--text-secondary); display: block; margin-top: 4px;">Occurred: <strong>${evt.time}</strong></span>
        </div>
        
        <p style="color: var(--text-secondary); margin-bottom: 20px; font-size: 0.95rem;">
          ${evt.desc}
        </p>

        <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid var(--panel-border); padding: 14px; border-radius: 12px; margin-bottom: 20px;">
          <h4 style="font-weight: 700; font-size: 0.85rem; text-transform: uppercase; color: var(--text-muted); margin-bottom: 8px;">Audit Metadata:</h4>
          <ul style="list-style: none; padding-left: 0; font-size: 0.82rem; color: var(--text-secondary); display: flex; flex-direction: column; gap: 6px;">
            <li>&bull; <strong>Initiated By:</strong> Shrikant Keche (CEO)</li>
            <li>&bull; <strong>IP Address:</strong> 192.168.10.42</li>
            <li>&bull; <strong>Security Level:</strong> RESTRICTED-CONFIDENTIAL</li>
            <li>&bull; <strong>Auth Hash:</strong> SHA-256 e8f3224b...</li>
          </ul>
        </div>

        <div style="display: flex; gap: 12px; justify-content: flex-end;">
          <button class="btn btn-secondary" onclick="document.getElementById('modalCloseBtn').click()">Close Details</button>
        </div>
      </div>
    `;
    openModal('Timeline Log Event', detailsHtml);
  };

  // --- Animated KPI Counters ---
  const animateCounter = (el, target, isCurrency = false, isPercent = false, duration = 1200) => {
    if (!el) return;
    let startTime = null;
    const step = (timestamp) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      const currentVal = progress * target;
      
      if (isCurrency) {
        el.textContent = formatIndianRupees(currentVal);
      } else if (isPercent) {
        el.textContent = currentVal.toFixed(1) + '%';
      } else {
        el.textContent = Math.floor(currentVal).toLocaleString('en-IN');
      }
      
      if (progress < 1) {
        window.requestAnimationFrame(step);
      } else {
        if (isCurrency) {
          el.textContent = formatIndianRupees(target);
        } else if (isPercent) {
          el.textContent = target.toFixed(1) + '%';
        } else {
          el.textContent = Math.floor(target).toLocaleString('en-IN');
        }
      }
    };
    window.requestAnimationFrame(step);
  };

  const triggerKpiAnimations = () => {
    const metrics = state.latestMetrics;
    animateCounter(kpiRev, metrics.revenue, true, false);
    animateCounter(kpiSales, metrics.sales, false, false);
    animateCounter(kpiCust, metrics.customers, false, false);
    animateCounter(kpiOrd, metrics.orders, false, false);
    animateCounter(kpiProf, metrics.profit, false, true);
    animateCounter(kpiGrow, metrics.growth, false, true);
  };

  // --- Render Tables ---
  const renderOrdersTable = (list) => {
    const dbOrdersBody = document.getElementById('dashboardOrdersTableBody');
    if (!dbOrdersBody) return;
    dbOrdersBody.innerHTML = '';
    
    // Only display 5 recent items on dashboard
    list.slice(0, 5).forEach(order => {
      const statusClass = order.status === 'Delivered' ? 'status-delivered' : (order.status === 'Pending' ? 'status-pending' : 'status-processing');
      const row = document.createElement('tr');
      row.innerHTML = `
        <td><strong>${order.id}</strong></td>
        <td>${order.name}</td>
        <td>${order.product}</td>
        <td><strong>${formatIndianRupees(order.amount)}</strong></td>
        <td><span class="badge-status ${statusClass}">${order.status}</span></td>
        <td>${order.date}</td>
      `;
      row.addEventListener('click', () => openOrderDetailsModal(order));
      dbOrdersBody.appendChild(row);
    });

    renderManagementTable(list);
  };

  const renderManagementTable = (list) => {
    const managementOrdersBody = document.getElementById('ordersManagementTableBody');
    if (!managementOrdersBody) return;
    managementOrdersBody.innerHTML = '';
    list.forEach(order => {
      const statusClass = order.status === 'Delivered' ? 'status-delivered' : (order.status === 'Pending' ? 'status-pending' : 'status-processing');
      const row = document.createElement('tr');
      row.innerHTML = `
        <td><strong>${order.id}</strong></td>
        <td>${order.name}</td>
        <td>${order.product}</td>
        <td><strong>${formatIndianRupees(order.amount)}</strong></td>
        <td><span class="badge-status ${statusClass}">${order.status}</span></td>
        <td>${order.date}</td>
        <td>
          <button class="txt-btn process-order-btn" data-id="${order.id}">Process</button>
        </td>
      `;
      row.addEventListener('click', (e) => {
        if (!e.target.classList.contains('process-order-btn')) {
          openOrderDetailsModal(order);
        }
      });
      managementOrdersBody.appendChild(row);
    });
  };

  // Populate activities logs from DB
  const populateTimeline = async () => {
    try {
      const activities = await fetch('/api/v1/activities').then(r => r.json());
      const timelineContainer = document.getElementById('activitiesTimeline');
      const timelineContainerFull = document.getElementById('activitiesTimelineFull');
      
      const renderItems = (container) => {
        if (!container) return;
        container.innerHTML = '';
        activities.forEach(evt => {
          const item = document.createElement('div');
          item.className = 'timeline-item';
          item.innerHTML = `
            <div class="timeline-dot"></div>
            <div class="timeline-content">
              <span class="timeline-title">${evt.title}</span>
              <span class="timeline-desc">${evt.desc}</span>
              <span class="timeline-time">${evt.time}</span>
            </div>
          `;
          item.addEventListener('click', () => openTimelineDetailsModal(evt));
          container.appendChild(item);
        });
      };

      renderItems(timelineContainer);
      renderItems(timelineContainerFull);
    } catch (e) {
      console.error("Failed to load activities", e);
    }
  };

  // Populating Alerts Compact list
  const populateAlertsCenter = async () => {
    try {
      const alerts = await fetch('/api/v1/alerts').then(r => r.json());
      const alertsContainer = document.getElementById('alertsCompactContainer');
      if (!alertsContainer) return;
      alertsContainer.innerHTML = '';
      alerts.forEach(alert => {
        const item = document.createElement('div');
        item.className = 'alert-compact-item';
        item.innerHTML = `
          <div class="alert-c-left">
            <div class="alert-c-indicator ${alert.type}"></div>
            <span class="alert-c-title">${alert.title}</span>
          </div>
          <span class="alert-c-tag ${alert.type}">${alert.tag}</span>
        `;
        item.addEventListener('click', () => openAlertDetailsModal(alert));
        alertsContainer.appendChild(item);
      });
    } catch (e) {
      console.error("Failed to load alerts", e);
    }
  };

  // Error fallback handler for charts
  const showChartError = (containerId, chartName) => {
    const container = document.getElementById(containerId);
    if (container) {
      container.innerHTML = `
        <div class="flex-center flex-column" style="height: 100%; min-height: 220px; color: var(--danger); font-family: var(--font-family); gap: 10px; padding: 20px; text-align: center;">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="opacity: 0.8;">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <span style="font-weight: 600; font-size: 0.9rem;">Failed to load ${chartName}</span>
          <span style="font-size: 0.78rem; color: var(--text-muted);">Could not fetch dynamic database data.</span>
        </div>
      `;
    }
  };

  // --- Render ApexCharts Async ---
  const renderAllCharts = async () => {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const gridColor = isDark ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)';
    const textLabelColor = isDark ? '#cbd5e1' : '#1e293b';
    
    Object.keys(chartInstances).forEach(key => {
      if (chartInstances[key]) {
        try {
          chartInstances[key].destroy();
        } catch (err) {}
        chartInstances[key] = null;
      }
    });

    const queryStr = buildQueryString();

    // 1. Monthly Sales Trend (Line/Area)
    try {
      const salesRes = await fetch(`/api/v1/chart/sales${queryStr}`).then(r => r.json());
      if (salesRes.error) throw new Error(salesRes.error);
      const container = document.querySelector("#salesTrendChartContainer");
      if (container) {
        container.innerHTML = "";
        const salesOptions = {
          chart: {
            height: 280,
            type: 'area',
            toolbar: { show: false },
            background: 'transparent',
            events: {
              dataPointSelection: (event, chartContext, config) => {
                if (config.dataPointIndex === undefined || config.dataPointIndex === null || config.dataPointIndex === -1) return;
                const label = config.w.globals.labels[config.dataPointIndex];
                const val = config.w.globals.series[0][config.dataPointIndex];

                const months = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
                // If clicking a month trend column, trigger drilldown
                if (label && (months.includes(label) || label.includes(' '))) {
                  const cleanLabel = label.split(' ').pop();
                  if (months.includes(cleanLabel)) {
                    state.filters.month = cleanLabel;
                    state.drillLevel = 'month';
                    updateDashboard();
                    showToast(`Filtered dashboard by month: ${cleanLabel}`, 'success');
                  }
                }

                const detailsHtml = `
                  <div style="font-family: var(--font-family); line-height: 1.6;">
                    <h4 style="margin-bottom: 12px; font-weight: 800; font-size: 1.15rem;">Sales Performance Details: ${label}</h4>
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                      <tr>
                        <td style="padding: 6px 0; color: var(--text-secondary); font-weight: 600;">Sales Volume:</td>
                        <td style="padding: 6px 0; font-weight: 700; text-align: right;">${val.toLocaleString()} units</td>
                      </tr>
                      <tr>
                        <td style="padding: 6px 0; color: var(--text-secondary); font-weight: 600;">Average Order Value:</td>
                        <td style="padding: 6px 0; font-weight: 700; text-align: right;">&#8377;12,400</td>
                      </tr>
                    </table>
                    <div style="display: flex; gap: 12px; justify-content: flex-end;">
                      <button class="btn btn-secondary" onclick="document.getElementById('modalCloseBtn').click()">Close</button>
                    </div>
                  </div>
                `;
                openModal('Sales Trend Analysis', detailsHtml);
              }
            }
          },
          colors: ['#4f46e5'],
          fill: {
            type: 'gradient',
            gradient: {
              shadeIntensity: 1,
              opacityFrom: 0.45,
              opacityTo: 0.05
            }
          },
          stroke: { curve: 'smooth', width: 3 },
          dataLabels: { enabled: false },
          series: [{ name: 'Sales Volume', data: salesRes.data }],
          xaxis: {
            categories: salesRes.categories,
            labels: { style: { colors: textLabelColor } }
          },
          yaxis: {
            labels: {
              style: { colors: textLabelColor },
              formatter: (val) => Math.floor(val).toLocaleString()
            }
          },
          grid: { borderColor: gridColor },
          theme: { mode: isDark ? 'dark' : 'light' }
        };

        chartInstances.sales = new ApexCharts(container, salesOptions);
        chartInstances.sales.render();
      }
    } catch (e) {
      console.error("Error rendering sales chart", e);
      showChartError("salesTrendChartContainer", "Monthly Sales Trend");
    }

    // 2. Revenue Distribution (Donut Chart)
    try {
      const regionRes = await fetch(`/api/v1/chart/region${queryStr}`).then(r => r.json());
      if (regionRes.error) throw new Error(regionRes.error);
      const container = document.querySelector("#revenueRegionChartContainer");
      if (container) {
        container.innerHTML = "";
        const regionOptions = {
          chart: {
            height: 300,
            type: 'donut',
            background: 'transparent',
            events: {
              dataPointSelection: (event, chartContext, config) => {
                if (config.dataPointIndex === undefined || config.dataPointIndex === null || config.dataPointIndex === -1) return;
                const label = config.w.globals.labels[config.dataPointIndex];
                const pct = config.w.globals.series[config.dataPointIndex];
                const amt = regionRes.amounts[config.dataPointIndex];

                if (state.filters.region === label) {
                  state.filters.region = null;
                  state.drillLevel = 'dashboard';
                  updateDashboard();
                  showToast(`Cleared region filter.`, 'info');
                  return;
                }

                state.filters.region = label;
                state.drillLevel = 'region';
                updateDashboard();
                showToast(`Filtered dashboard by region: ${label}`, 'success');

                const detailsHtml = `
                  <div style="font-family: var(--font-family); line-height: 1.6;">
                    <h4 style="margin-bottom: 12px; font-weight: 800; font-size: 1.15rem;">Regional Performance: ${label}</h4>
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                      <tr>
                        <td style="padding: 6px 0; color: var(--text-secondary); font-weight: 600;">Revenue Share:</td>
                        <td style="padding: 6px 0; font-weight: 700; text-align: right; color: var(--primary);">${pct}%</td>
                      </tr>
                      <tr>
                        <td style="padding: 6px 0; color: var(--text-secondary); font-weight: 600;">Total Revenue:</td>
                        <td style="padding: 6px 0; font-weight: 700; text-align: right;">${formatIndianRupees(amt)}</td>
                      </tr>
                    </table>
                    <div style="display: flex; gap: 12px; justify-content: flex-end;">
                      <button class="btn btn-secondary" onclick="document.getElementById('modalCloseBtn').click()">Close</button>
                    </div>
                  </div>
                `;
                openModal('Regional Analysis', detailsHtml);
              }
            }
          },
          labels: regionRes.labels,
          series: regionRes.series,
          colors: getRegionColors(isDark),
          stroke: { show: true, width: 2, colors: [isDark ? '#1e1b4b' : '#ffffff'] },
          plotOptions: {
            pie: {
              donut: {
                size: '72%',
                labels: {
                  show: true,
                  name: { show: true, fontSize: '0.85rem', color: textLabelColor, fontWeight: 600 },
                  value: {
                    show: true,
                    fontSize: '1.2rem',
                    fontWeight: 800,
                    color: textLabelColor,
                    formatter: val => `${val}%`
                  },
                  total: {
                    show: true,
                    label: state.filters.region ? 'Selected Region' : 'Top Region',
                    fontSize: '0.8rem',
                    color: 'var(--text-secondary)',
                    formatter: w => {
                      if (state.filters.region) {
                        return state.filters.region;
                      }
                      const series = w.globals.series;
                      const maxVal = Math.max(...series);
                      const idx = series.indexOf(maxVal);
                      return w.globals.labels[idx] || '';
                    }
                  }
                }
              }
            }
          },
          legend: { show: false },
          theme: { mode: isDark ? 'dark' : 'light' }
        };

        chartInstances.region = new ApexCharts(container, regionOptions);
        chartInstances.region.render();
      }
    } catch (e) {
      console.error("Error rendering region chart", e);
      showChartError("revenueRegionChartContainer", "Revenue Distribution by Region");
    }

    // 3. Customer Growth Analytics (Stacked Bar)
    try {
      const custRes = await fetch(`/api/v1/chart/customers${queryStr}`).then(r => r.json());
      if (custRes.error) throw new Error(custRes.error);
      const container = document.querySelector("#customerGrowthChartContainer");
      if (container) {
        container.innerHTML = "";
        const customerOptions = {
          chart: {
            type: 'bar',
            height: 280,
            stacked: true,
            toolbar: { show: false },
            background: 'transparent',
            events: {
              dataPointSelection: (event, chartContext, config) => {
                if (config.dataPointIndex === undefined || config.dataPointIndex === null || config.dataPointIndex === -1) return;
                const label = config.w.globals.labels[config.dataPointIndex];
                const segName = config.seriesIndex === 0 ? 'New Clients' : 'Returning';
                const val = config.w.globals.series[config.seriesIndex][config.dataPointIndex];

                state.filters.segment = segName;
                state.drillLevel = 'customer';
                updateDashboard();
                showToast(`Filtered dashboard by segment: ${segName}`, 'success');

                const detailsHtml = `
                  <div style="font-family: var(--font-family); line-height: 1.6;">
                    <h4 style="margin-bottom: 12px; font-weight: 800; font-size: 1.15rem;">Customer Group Details: ${label}</h4>
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                      <tr>
                        <td style="padding: 6px 0; color: var(--text-secondary); font-weight: 600;">Segment Name:</td>
                        <td style="padding: 6px 0; font-weight: 700; text-align: right; color: var(--secondary);">${segName}</td>
                      </tr>
                      <tr>
                        <td style="padding: 6px 0; color: var(--text-secondary); font-weight: 600;">Accounts Count:</td>
                        <td style="padding: 6px 0; font-weight: 700; text-align: right;">${val.toLocaleString()}</td>
                      </tr>
                    </table>
                    <div style="display: flex; gap: 12px; justify-content: flex-end;">
                      <button class="btn btn-secondary" onclick="document.getElementById('modalCloseBtn').click()">Close</button>
                    </div>
                  </div>
                `;
                openModal('Customer Growth Insights', detailsHtml);
              }
            }
          },
          colors: getCustomerColors(isDark),
          plotOptions: { bar: { horizontal: false, columnWidth: '45%', borderRadius: 4 } },
          series: [
            { name: 'New Clients', data: custRes.new_clients },
            { name: 'Returning', data: custRes.returning }
          ],
          xaxis: {
            categories: custRes.categories,
            labels: { style: { colors: textLabelColor } }
          },
          yaxis: { labels: { style: { colors: textLabelColor } } },
          grid: { borderColor: gridColor },
          legend: { show: false },
          theme: { mode: isDark ? 'dark' : 'light' }
        };

        chartInstances.customers = new ApexCharts(container, customerOptions);
        chartInstances.customers.render();
      }
    } catch (e) {
      console.error("Error rendering customers chart", e);
      showChartError("customerGrowthChartContainer", "Customer Growth Analytics");
    }

    // 4. Profit & Expense Analysis (Combo Bar/Line)
    try {
      const profitRes = await fetch(`/api/v1/chart/profit${queryStr}`).then(r => r.json());
      if (profitRes.error) throw new Error(profitRes.error);
      const container = document.querySelector("#profitAnalysisChartContainer");
      if (container) {
        container.innerHTML = "";
        const profitOptions = {
          chart: {
            height: 280,
            type: 'line',
            toolbar: { show: false },
            background: 'transparent'
          },
          colors: ['#4f46e5', '#ef4444', '#10b981'],
          stroke: { width: [0, 0, 3], curve: 'smooth' },
          plotOptions: { bar: { columnWidth: '50%', borderRadius: 4 } },
          series: [
            { name: 'Revenue', type: 'bar', data: profitRes.revenue },
            { name: 'Expenses', type: 'bar', data: profitRes.expense },
            { name: 'Net Profit', type: 'line', data: profitRes.profit }
          ],
          fill: {
            opacity: [0.85, 0.85, 1],
            gradient: {
              inverseColors: false,
              shade: 'light',
              type: "vertical",
              opacityFrom: 0.85,
              opacityTo: 0.55
            }
          },
          xaxis: {
            categories: profitRes.categories,
            labels: { style: { colors: textLabelColor } }
          },
          yaxis: {
            labels: {
              style: { colors: textLabelColor },
              formatter: (val) => formatIndianRupees(val)
            }
          },
          tooltip: {
            y: {
              formatter: (val) => formatIndianRupees(val)
            }
          },
          grid: { borderColor: gridColor },
          legend: { show: false },
          theme: { mode: isDark ? 'dark' : 'light' }
        };

        chartInstances.profit = new ApexCharts(container, profitOptions);
        chartInstances.profit.render();
      }
    } catch (e) {
      console.error("Error rendering profit chart", e);
      showChartError("profitAnalysisChartContainer", "Profit & Expense Analysis");
    }

    // 5. System Health KPI Gauge (Radial Bar)
    try {
      const healthContainer = document.querySelector("#healthGaugeContainer");
      const hs = state.latestMetrics && state.latestMetrics.healthScore !== null ? state.latestMetrics.healthScore : null;
      if (healthContainer && hs !== null) {
        healthContainer.innerHTML = "";
        let color = '#10b981';
        if (hs < 50) color = '#ef4444';
        else if (hs < 80) color = '#f59e0b';
        
        const healthOptions = {
          chart: {
            height: 190,
            type: 'radialBar',
            background: 'transparent'
          },
          plotOptions: {
            radialBar: {
              startAngle: -135,
              endAngle: 135,
              dataLabels: {
                name: { show: false },
                value: {
                  color: textLabelColor,
                  show: true,
                  offsetY: 6,
                  formatter: val => `${val}`
                }
              },
              track: {
                background: gridColor
              }
            }
          },
          colors: [color],
          series: [hs],
          theme: { mode: isDark ? 'dark' : 'light' }
        };
        chartInstances.healthGauge = new ApexCharts(healthContainer, healthOptions);
        chartInstances.healthGauge.render();
      }
    } catch (e) {
      console.error("Error rendering health gauge", e);
    }

    // 6. Revenue Breakdown by Category (Sub-View Product Bar Chart)
    try {
      const revBreakdownEl = document.querySelector("#revenueBreakdownChart");
      if (revBreakdownEl) {
        revBreakdownEl.innerHTML = "";
        const totalRev = state.latestMetrics.revenue;
        const productShares = [0.40, 0.28, 0.20, 0.12];
        const productData = productShares.map(s => Math.floor(totalRev * s));

        const breakdownOptions = {
          chart: { 
            type: 'bar', 
            height: 320, 
            toolbar: { show: false }, 
            background: 'transparent',
            events: {
              dataPointSelection: (event, chartContext, config) => {
                if (config.dataPointIndex === undefined || config.dataPointIndex === null || config.dataPointIndex === -1) return;
                const label = config.w.globals.labels[config.dataPointIndex];
                let productName = label;
                state.filters.product = productName;
                updateDashboard();
                showToast(`Filtered dashboard by product: ${productName}`, 'success');
              }
            }
          },
          colors: getProductColors(isDark),
          plotOptions: { 
            bar: { 
              borderRadius: 4,
              distributed: true
            } 
          },
          series: [{ name: 'Income Source', data: productData }],
          xaxis: {
            categories: ['Apple iPhone 16', 'MacBook Air M4', 'Samsung Galaxy S25', 'Dell XPS 15'],
            labels: { style: { colors: textLabelColor } }
          },
          yaxis: {
            labels: {
              style: { colors: textLabelColor },
              formatter: (val) => formatIndianRupees(val)
            }
          },
          tooltip: {
            y: {
              formatter: (val) => formatIndianRupees(val)
            }
          },
          grid: { borderColor: gridColor },
          theme: { mode: isDark ? 'dark' : 'light' }
        };
        chartInstances.revenueBreakdown = new ApexCharts(revBreakdownEl, breakdownOptions);
        chartInstances.revenueBreakdown.render();
      }
    } catch (e) {
      console.error("Error rendering revenue breakdown chart", e);
    }

    // 7. Sales Funnel & Pipeline Forecast (Sub-View Charts)
    try {
      const salesFunnelEl = document.querySelector("#salesFunnelChart");
      if (salesFunnelEl) {
        salesFunnelEl.innerHTML = "";
        const funnelOptions = {
          chart: { type: 'bar', height: 280, toolbar: { show: false }, background: 'transparent' },
          colors: ['#06b6d4'],
          plotOptions: { bar: { horizontal: true, borderRadius: 4 } },
          series: [{ name: 'Leads Count', data: [1200, 850, 600, 420, 180] }],
          xaxis: {
            categories: ['Awareness', 'Interest', 'Evaluation', 'Negotiation', 'Closed Won'],
            labels: { style: { colors: textLabelColor } }
          },
          yaxis: { labels: { style: { colors: textLabelColor } } },
          grid: { borderColor: gridColor },
          theme: { mode: isDark ? 'dark' : 'light' }
        };
        chartInstances.salesFunnel = new ApexCharts(salesFunnelEl, funnelOptions);
        chartInstances.salesFunnel.render();
      }
    } catch (e) {
      console.error("Error rendering sales funnel chart", e);
    }

    try {
      const salesPipelineEl = document.querySelector("#salesPipelineChart");
      if (salesPipelineEl) {
        salesPipelineEl.innerHTML = "";
        const pipelineOptions = {
          chart: { type: 'line', height: 280, toolbar: { show: false }, background: 'transparent' },
          colors: ['#4f46e5'],
          series: [{ name: 'Projected Value (₹)', data: [12000000, 14000000, 17000000, 21000000, 25000000] }],
          xaxis: {
            categories: ['Jul', 'Aug', 'Sep', 'Oct', 'Nov'],
            labels: { style: { colors: textLabelColor } }
          },
          yaxis: {
            labels: {
              style: { colors: textLabelColor },
              formatter: (val) => formatIndianRupees(val)
            }
          },
          tooltip: {
            y: {
              formatter: (val) => formatIndianRupees(val)
            }
          },
          grid: { borderColor: gridColor },
          theme: { mode: isDark ? 'dark' : 'light' }
        };
        chartInstances.salesPipeline = new ApexCharts(salesPipelineEl, pipelineOptions);
        chartInstances.salesPipeline.render();
      }
    } catch (e) {
      console.error("Error rendering sales pipeline chart", e);
    }

    // 8. Customer Retention Rate Trend (Customer Sub-View)
    try {
      const customerRetentionEl = document.querySelector("#customerRetentionChart");
      if (customerRetentionEl) {
        customerRetentionEl.innerHTML = "";
        const retentionOptions = {
          chart: { type: 'line', height: 280, toolbar: { show: false }, background: 'transparent' },
          colors: ['#06b6d4'],
          series: [{ name: 'Retention Rate (%)', data: [91.2, 92.4, 91.8, 93.5, 94.2, 95.8] }],
          xaxis: {
            categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            labels: { style: { colors: textLabelColor } }
          },
          yaxis: { labels: { style: { colors: textLabelColor } } },
          grid: { borderColor: gridColor },
          theme: { mode: isDark ? 'dark' : 'light' }
        };
        chartInstances.customerRetention = new ApexCharts(customerRetentionEl, retentionOptions);
        chartInstances.customerRetention.render();
      }
    } catch (e) {
      console.error("Error rendering customer retention chart", e);
    }

    // 9. Forecast Confidence Curve (AI View) — rendered by renderAiInsightsPage
    // (No static hardcoded chart here — rendered dynamically from API data)

    // 10. Customer Satisfaction NPS Gauge (Radial Bar)
    try {
      const npsContainer = document.querySelector("#npsGaugeContainer");
      if (npsContainer) {
        npsContainer.innerHTML = "";
        const npsVal = state.latestMetrics ? Math.round(state.latestMetrics.nps) : 78;
        
        const npsOptions = {
          chart: {
            height: 190,
            type: 'radialBar',
            background: 'transparent'
          },
          plotOptions: {
            radialBar: {
              startAngle: -135,
              endAngle: 135,
              hollow: {
                size: '72%'
              },
              track: {
                background: isDark ? '#334155' : '#e2e8f0',
                strokeWidth: '97%'
              },
              dataLabels: {
                name: {
                  show: true,
                  fontSize: '0.8rem',
                  color: 'var(--text-secondary)',
                  offsetY: -10
                },
                value: {
                  show: true,
                  fontSize: '1.4rem',
                  fontWeight: 800,
                  color: textLabelColor,
                  offsetY: 4,
                  formatter: val => val
                }
              }
            }
          },
          fill: {
            type: 'gradient',
            gradient: {
              shade: 'dark',
              type: 'horizontal',
              gradientToColors: ['#06b6d4'],
              inverseColors: false,
              opacityFrom: 1,
              opacityTo: 1,
              stops: [0, 100]
            }
          },
          colors: ['#4f46e5'],
          stroke: {
            lineCap: 'round'
          },
          labels: ['NPS Score'],
          series: [npsVal],
          theme: { mode: isDark ? 'dark' : 'light' }
        };
        
        chartInstances.nps = new ApexCharts(npsContainer, npsOptions);
        chartInstances.nps.render();
      }
    } catch (e) {
      console.error("Error rendering NPS gauge chart", e);
    }
  };

  // Sales Trend chart control toggle Line/Area
  const lineBtn = document.getElementById('btnSalesLine');
  const areaBtn = document.getElementById('btnSalesArea');
  if (lineBtn && areaBtn) {
    lineBtn.addEventListener('click', () => {
      lineBtn.classList.add('active');
      areaBtn.classList.remove('active');
      chartInstances.sales.updateOptions({
        chart: { type: 'line' },
        fill: { type: 'solid', opacity: 1 }
      });
    });
    areaBtn.addEventListener('click', () => {
      areaBtn.classList.add('active');
      lineBtn.classList.remove('active');
      chartInstances.sales.updateOptions({
        chart: { type: 'area' },
        fill: {
          type: 'gradient',
          gradient: {
            shadeIntensity: 1,
            opacityFrom: 0.45,
            opacityTo: 0.05
          }
        }
      });
    });
  }

  // --- Views Router Implementation ---
  const switchView = (targetViewId) => {
    views.forEach(v => {
      v.classList.remove('active-view');
    });
    const selectedView = document.getElementById(`view-${targetViewId}`);
    if (selectedView) {
      selectedView.classList.add('active-view');
      if (targetViewId === 'dashboard') {
        triggerKpiAnimations();
      }
      window.dispatchEvent(new Event('resize'));
    }

    navItems.forEach(item => {
      if (item.getAttribute('data-view') === targetViewId) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });

    sidebar.classList.remove('mobile-open');
  };

  navItems.forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const targetView = item.getAttribute('data-view');
      if (targetView) {
        switchView(targetView);
      }
    });
  });

  viewSwitchTriggers.forEach(trig => {
    trig.addEventListener('click', (e) => {
      e.preventDefault();
      const target = trig.getAttribute('data-target-view');
      if (target) {
        switchView(target);
      }
    });
  });

  // --- Sidebar & Navigation UI Trigger handlers ---
  sidebarToggleBtn.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
    if (sidebar.classList.contains('collapsed')) {
      sidebar.style.width = '80px';
      contentWrapper.style.marginLeft = '80px';
      sidebar.querySelectorAll('.logo-text, .nav-section, .nav-link span, .user-details, .badge').forEach(el => {
        el.style.display = 'none';
      });
      sidebar.querySelector('.sidebar-header').style.justifyContent = 'center';
      sidebar.querySelector('.sidebar-user-panel').style.justifyContent = 'center';
    } else {
      sidebar.style.width = '280px';
      contentWrapper.style.marginLeft = '280px';
      sidebar.querySelectorAll('.logo-text, .nav-link span, .user-details, .badge').forEach(el => {
        el.style.display = 'inline';
      });
      sidebar.querySelectorAll('.nav-section').forEach(el => {
        el.style.display = 'block';
      });
      sidebar.querySelector('.sidebar-header').style.justifyContent = 'space-between';
      sidebar.querySelector('.sidebar-user-panel').style.justifyContent = 'flex-start';
    }
    window.dispatchEvent(new Event('resize'));
  });

  mobileToggleBtn.addEventListener('click', () => {
    sidebar.classList.toggle('mobile-open');
  });

  document.addEventListener('click', (e) => {
    if (window.innerWidth <= 768) {
      if (!sidebar.contains(e.target) && !mobileToggleBtn.contains(e.target)) {
        sidebar.classList.remove('mobile-open');
      }
    }
  });

  profileTrigger.addEventListener('click', (e) => {
    e.stopPropagation();
    profileDropdown.classList.toggle('active');
    notifDropdown.classList.remove('active');
  });

  notifBell.addEventListener('click', (e) => {
    e.stopPropagation();
    notifDropdown.classList.toggle('active');
    profileDropdown.classList.remove('active');
  });

  document.addEventListener('click', () => {
    profileDropdown.classList.remove('active');
    notifDropdown.classList.remove('active');
  });

  clearAllNotifBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    dropdownNotifList.innerHTML = `
      <div style="padding: 20px; text-align: center; color: var(--text-muted); font-size: 0.82rem;">
        No active alerts.
      </div>
    `;
    showToast('All notifications cleared.', 'success');
  });

  // --- Export Report Functional Events ---
  const loadJsPDF = () => {
    return new Promise((resolve, reject) => {
      if (window.jspdf) {
        resolve(window.jspdf);
        return;
      }
      const script = document.createElement('script');
      script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js';
      script.onload = () => resolve(window.jspdf);
      script.onerror = (e) => reject(e);
      document.head.appendChild(script);
    });
  };

    document.getElementById('exportCSVBtn').addEventListener('click', async () => {
    showToast('Generating CSV report...', 'info');
    try {
      const queryStr = buildQueryString();
      const metrics = state.latestMetrics || {};
      const apiBase = window.location.pathname.substring(0, window.location.pathname.lastIndexOf('/')) || '';
      const orders = await fetch(`${apiBase}/api/v1/orders${queryStr}`).then(r => r.json());
      
      let csvContent = "INSIGHTHUB EXECUTIVE SUMMARY REPORT\n";
      csvContent += `Generated Date,${new Date().toLocaleString()}\n`;
      csvContent += `Filters applied,Region: ${state.filters.region || 'All'},Month: ${state.filters.month || 'All'},Segment: ${state.filters.segment || 'All'},Product: ${state.filters.product || 'All'},Period: ${state.filters.period || 'All'}\n\n`;
      
      const revenue = metrics.revenue !== undefined && metrics.revenue !== null ? metrics.revenue : 0;
      const sales = metrics.sales !== undefined && metrics.sales !== null ? metrics.sales : 0;
      const customers = metrics.customers !== undefined && metrics.customers !== null ? metrics.customers : 0;
      const ordersCount = metrics.orders !== undefined && metrics.orders !== null ? metrics.orders : 0;
      const profit = metrics.profit !== undefined && metrics.profit !== null ? metrics.profit : 0;
      const growth = metrics.growth !== undefined && metrics.growth !== null ? metrics.growth : 0;
      const nps = metrics.nps !== undefined && metrics.nps !== null ? metrics.nps : 0;

      csvContent += "METRIC,VALUE\n";
      csvContent += `Total Revenue,₹${revenue.toFixed(2)}\n`;
      csvContent += `Total Sales,${sales}\n`;
      csvContent += `Total Customers,${customers}\n`;
      csvContent += `Total Orders,${ordersCount}\n`;
      csvContent += `Profit Margin,${profit.toFixed(1)}%\n`;
      csvContent += `Growth Rate,${growth.toFixed(1)}%\n`;
      csvContent += `NPS Score,${nps.toFixed(0)}\n\n`;
      
      csvContent += "DETAILED TRANSACTIONS (FILTERED)\n";
      csvContent += "Order ID,Customer Name,Product,Amount (INR),Status,Date,Region,Month,Customer Segment\n";
      
      (orders.data || orders).forEach(o => {
        const name = `"${o.name.replace(/"/g, '""')}"`;
        const prod = `"${o.product.replace(/"/g, '""')}"`;
        csvContent += `${o.id},${name},${prod},${o.amount},${o.status},${o.date},${o.region},${o.month},${o.segment}\n`;
      });
      
      const today = new Date();
      const day = String(today.getDate()).padStart(2, '0');
      const month = String(today.getMonth() + 1).padStart(2, '0');
      const year = today.getFullYear();
      const filename = `Business_Report_${day}-${month}-${year}.csv`;
      
      // Prepend BOM to ensure Excel opens CSV as UTF-8 on Windows
      const blob = new Blob(["\uFEFF" + csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.setAttribute("href", url);
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      showToast('CSV downloaded successfully', 'success');
    } catch (err) {
      console.error("CSV Export failed", err);
      showToast('Failed to export CSV', 'danger');
    }
  });

  document.getElementById('downloadReportBtn').addEventListener('click', async () => {
    showToast('Generating PDF report...', 'info');
    try {
      const jspdfModule = await loadJsPDF();
      const { jsPDF } = window.jspdf;
      const doc = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: 'a4'
      });

      const metrics = state.latestMetrics || {};
      const today = new Date();
      const day = String(today.getDate()).padStart(2, '0');
      const month = String(today.getMonth() + 1).padStart(2, '0');
      const year = today.getFullYear();
      const dateStr = `${day}-${month}-${year}`;
      const timeStr = today.toLocaleTimeString();

      doc.setProperties({
        title: `InsightHub Executive Report ${dateStr}`,
        author: 'InsightHub Analytics'
      });

      const primaryColor = [79, 70, 229]; // #4f46e5 (Indigo)
      const secondaryColor = [6, 182, 212]; // #06b6d4 (Cyan)
      const darkColor = [30, 41, 59]; // Slate 800
      const lightGrey = [241, 245, 249]; // Slate 100
      const borderGrey = [226, 232, 240]; // Slate 200

      // Header Background
      doc.setFillColor(...primaryColor);
      doc.rect(0, 0, 210, 40, 'F');

      // Header Title
      doc.setTextColor(255, 255, 255);
      doc.setFont("helvetica", "bold");
      doc.setFontSize(22);
      doc.text("INSIGHTHUB EXECUTIVE SUMMARY", 15, 18);

      doc.setFont("helvetica", "normal");
      doc.setFontSize(10);
      doc.text(`Report Generated: ${dateStr} at ${timeStr}`, 15, 25);
      
      const activeFilters = `Filters: Region: ${state.filters.region || 'All'} | Month: ${state.filters.month || 'All'} | Segment: ${state.filters.segment || 'All'} | Product: ${state.filters.product || 'All'} | Period: ${state.filters.period || 'All'}`;
      doc.text(activeFilters, 15, 31);

      // Section 1: KPI Summary Card Grid
      doc.setTextColor(...darkColor);
      doc.setFont("helvetica", "bold");
      doc.setFontSize(14);
      doc.text("Key Performance Indicators (KPIs)", 15, 52);
      
      doc.setDrawColor(...borderGrey);
      doc.line(15, 55, 195, 55);

      const revenue = metrics.revenue !== undefined && metrics.revenue !== null ? metrics.revenue : 0;
      const sales = metrics.sales !== undefined && metrics.sales !== null ? metrics.sales : 0;
      const customers = metrics.customers !== undefined && metrics.customers !== null ? metrics.customers : 0;
      const ordersCount = metrics.orders !== undefined && metrics.orders !== null ? metrics.orders : 0;
      const profit = metrics.profit !== undefined && metrics.profit !== null ? metrics.profit : 0;
      const growth = metrics.growth !== undefined && metrics.growth !== null ? metrics.growth : 0;
      const nps = metrics.nps !== undefined && metrics.nps !== null ? metrics.nps : 0;

      const kpis = [
        { label: "Total Revenue", val: `INR ${revenue.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` },
        { label: "Total Sales Count", val: `${sales.toLocaleString('en-IN')}` },
        { label: "Total Customer Count", val: `${customers.toLocaleString('en-IN')}` },
        { label: "Total Orders Count", val: `${ordersCount.toLocaleString('en-IN')}` },
        { label: "Average Profit Margin", val: `${profit.toFixed(1)}%` },
        { label: "Growth Rate", val: `${growth.toFixed(1)}%` },
        { label: "Customer NPS Score", val: `${nps.toFixed(0)}` }
      ];

      let startY = 62;
      doc.setFont("helvetica", "bold");
      doc.setFontSize(10);
      doc.setFillColor(...lightGrey);

      kpis.forEach((kpi, idx) => {
        const row = Math.floor(idx / 2);
        const col = idx % 2;
        const x = 15 + col * 92;
        const yCoord = startY + row * 18;

        doc.setFillColor(...lightGrey);
        doc.rect(x, yCoord, 88, 14, 'F');
        doc.setDrawColor(...borderGrey);
        doc.rect(x, yCoord, 88, 14, 'S');

        doc.setTextColor(100, 116, 139); // Slate 500
        doc.setFont("helvetica", "normal");
        doc.setFontSize(8);
        doc.text(kpi.label, x + 4, yCoord + 5);

        doc.setTextColor(...darkColor);
        doc.setFont("helvetica", "bold");
        doc.setFontSize(10);
        doc.text(kpi.val, x + 4, yCoord + 10);
      });

      let y = 138;
      const checkPageOverflow = (heightNeeded) => {
        if (y + heightNeeded > 270) {
          doc.addPage();
          y = 25; // Top margin for new page
          
          // Draw header on new page
          doc.setFont("helvetica", "bold");
          doc.setFontSize(10);
          doc.setTextColor(79, 70, 229); // Primary color
          doc.text("InsightHub Executive Summary", 15, 15);
          doc.setDrawColor(226, 232, 240); // Border grey
          doc.line(15, 18, 195, 18);
        }
      };

      // Section 2: AI Strategic Insights
      checkPageOverflow(15);
      doc.setTextColor(...darkColor);
      doc.setFont("helvetica", "bold");
      doc.setFontSize(14);
      doc.text("AI Strategic Insights", 15, y);
      doc.setDrawColor(...borderGrey);
      doc.line(15, y + 3, 195, y + 3);
      y += 10;

      const aiRevText = document.getElementById('ai-insight-revenue')?.innerText || '';
      const aiCustText = document.getElementById('ai-insight-customers')?.innerText || '';
      const aiSalesText = document.getElementById('ai-insight-sales')?.innerText || '';
      const aiRecText = document.getElementById('ai-insight-recommendations')?.innerText || '';

      const insights = [
        { title: "Revenue Analysis", text: aiRevText },
        { title: "Customer Analysis", text: aiCustText },
        { title: "Sales Analysis", text: aiSalesText },
        { title: "Recommendations", text: aiRecText }
      ];

      insights.forEach(ins => {
        const descLines = doc.splitTextToSize(ins.text, 180);
        const heightNeeded = 4 + descLines.length * 3.5 + 5;
        
        checkPageOverflow(heightNeeded);
        
        doc.setFont("helvetica", "bold");
        doc.setFontSize(9);
        doc.setTextColor(...primaryColor);
        doc.text(ins.title, 15, y);

        doc.setFont("helvetica", "normal");
        doc.setFontSize(8);
        doc.setTextColor(...darkColor);
        doc.text(descLines, 15, y + 4);
        
        y += 4 + descLines.length * 3.5 + 4;
      });

      // Section 3: Critical Business Alerts
      const apiBase = window.location.pathname.substring(0, window.location.pathname.lastIndexOf('/')) || '';
      const alerts = await fetch(`${apiBase}/api/v1/alerts`).then(r => r.json());
      
      checkPageOverflow(15);
      doc.setTextColor(...darkColor);
      doc.setFont("helvetica", "bold");
      doc.setFontSize(14);
      doc.text("Critical Business Alerts", 15, y);
      doc.setDrawColor(...borderGrey);
      doc.line(15, y + 3, 195, y + 3);
      y += 10;
      
      if (alerts.length === 0) {
        checkPageOverflow(10);
        doc.setFont("helvetica", "italic");
        doc.setFontSize(9);
        doc.setTextColor(148, 163, 184); // Slate 400
        doc.text("No active critical alerts.", 15, y);
        y += 10;
      } else {
        alerts.forEach(al => {
          const descLines = doc.splitTextToSize(al.desc, 155);
          const heightNeeded = Math.max(5, descLines.length * 3.5 + 4) + 4;
          
          checkPageOverflow(heightNeeded);
          
          doc.setFont("helvetica", "bold");
          doc.setFontSize(8);
          doc.setTextColor(239, 68, 68); // Red
          doc.text(`[${al.tag.toUpperCase()}]`, 15, y);
          
          doc.setTextColor(...darkColor);
          doc.setFont("helvetica", "bold");
          doc.text(al.title, 38, y);
          
          doc.setFont("helvetica", "normal");
          doc.text(descLines, 38, y + 4);
          
          y += Math.max(5, descLines.length * 3.5 + 4) + 4;
        });
      }

      // Add footers dynamically
      const pageCount = doc.internal.getNumberOfPages();
      for (let i = 1; i <= pageCount; i++) {
        doc.setPage(i);
        doc.setFont("helvetica", "normal");
        doc.setFontSize(8);
        doc.setTextColor(148, 163, 184); // Slate 400
        doc.text("InsightHub Business Intelligence System - Confidential Report", 15, 285);
        doc.text(`Page ${i} of ${pageCount}`, 185, 285);
      }

      const filename = `Business_Report_${dateStr}.pdf`;
      doc.save(filename);
      showToast('PDF downloaded successfully', 'success');
    } catch (err) {
      console.error("PDF Export failed", err);
      showToast('Failed to export PDF', 'danger');
    }
  });// --- Order Search & Filter ---
  const statusFilter = document.getElementById('orderStatusFilter');
  const searchInputTable = document.getElementById('orderTableSearch');

  const filterOrdersTable = async () => {
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
  };

  if (statusFilter && searchInputTable) {
    statusFilter.addEventListener('change', filterOrdersTable);
    searchInputTable.addEventListener('input', filterOrdersTable);
  }

  // Action Button Process Order
  document.addEventListener('click', async (e) => {
    if (e.target.classList.contains('process-order-btn')) {
      const ordId = e.target.getAttribute('data-id');
      try {
        const res = await fetch('/api/v1/orders/process', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ order_id: ordId })
        }).then(r => r.json());
        
        if (res.success) {
          showToast(`Order ${ordId} status updated to ${res.new_status}!`, 'success');
          updateDashboard();
        } else {
          showToast(res.error || 'Failed to update order', 'danger');
        }
      } catch (err) {
        showToast('Connection failed.', 'danger');
      }
    }
  });

  // Global search bar filter navigation
  const globalSearchInput = document.getElementById('searchInput');
  const globalSearchResults = document.getElementById('searchResults');
  
  const searchPagesList = [
    { title: 'Dashboard Statistics Overview', view: 'dashboard' },
    { title: 'Revenue Analytics and Subscriptions', view: 'revenue' },
    { title: 'Sales Funnel and Projections', view: 'sales' },
    { title: 'Customer Demographics and NPS Feedback', view: 'customers' },
    { title: 'Orders System and Invoices', view: 'orders' },
    { title: 'System Monitors and Warning Alerts', view: 'alerts' },
    { title: 'AI Predictive Growth insights', view: 'ai-insights' },
    { title: 'Profile and Configuration settings', view: 'settings' }
  ];

  globalSearchInput.addEventListener('input', () => {
    const val = globalSearchInput.value.toLowerCase();
    if (!val) {
      globalSearchResults.style.display = 'none';
      return;
    }

    const matches = searchPagesList.filter(p => p.title.toLowerCase().includes(val));
    globalSearchResults.innerHTML = '';
    
    if (matches.length === 0) {
      globalSearchResults.innerHTML = `<div class="search-result-item" style="color: var(--text-muted); cursor: default;">No pages found</div>`;
    } else {
      matches.forEach(m => {
        const div = document.createElement('div');
        div.className = 'search-result-item';
        div.textContent = m.title;
        div.addEventListener('click', () => {
          switchView(m.view);
          globalSearchInput.value = '';
          globalSearchResults.style.display = 'none';
        });
        globalSearchResults.appendChild(div);
      });
    }
    globalSearchResults.style.display = 'block';
  });

  document.addEventListener('click', (e) => {
    if (!globalSearchInput.contains(e.target) && !globalSearchResults.contains(e.target)) {
      globalSearchResults.style.display = 'none';
    }
  });

  // Load profile settings initially
  const loadProfileSettings = async () => {
    try {
      const settings = await fetch('/api/v1/settings').then(r => r.json());
      document.getElementById('set-name').value = settings.name;
      document.getElementById('set-email').value = settings.email || '';
      
      const displayUser = settings.username || settings.name || 'User';
      document.querySelector('.profile-name').textContent = displayUser;
      document.querySelector('.user-full-name').textContent = 'Username: ' + displayUser + (settings.role ? ' | Role: ' + settings.role : '');
      
      if (document.querySelector('.user-email')) {
        document.querySelector('.user-email').style.display = 'none';
      }
      
      const sidebarPanel = document.querySelector('.sidebar-user-panel .user-name');
      if (sidebarPanel) sidebarPanel.textContent = displayUser;

      // Calculate dynamic initials based on username
      let initials = '??';
      const usrLower = displayUser.toLowerCase();
      if (usrLower === 'shrikant') {
          initials = 'SK';
      } else if (usrLower === 'manager') {
          initials = 'MG';
      } else if (usrLower === 'analyst') {
          initials = 'AN';
      } else {
          if (displayUser.length >= 2) {
              initials = displayUser.substring(0, 2).toUpperCase();
          } else if (displayUser.length === 1) {
              initials = displayUser.substring(0, 1).toUpperCase();
          }
      }
      
      // Update all avatar circles (navbar and sidebar)
      document.querySelectorAll('.avatar-circle').forEach(el => {
          el.textContent = initials;
      });
    } catch (e) {
      console.error("Failed to load settings", e);
    }
  };

  
  // Load User Management
  const loadUserManagement = async () => {
    try {
      const res = await fetch('/api/v1/users');
      if (res.ok) {
        const users = await res.json();
        const tbody = document.getElementById('user-mgmt-tbody');
        if (tbody) {
          tbody.innerHTML = users.map(u => `
            <tr>
              <td>${u.id}</td>
              <td class="font-mono">${u.username}</td>
              <td class="font-mono" style="color: var(--text-muted);">••••••••</td>
              <td><span class="role-badge role-${u.role.toLowerCase()}">${u.role}</span></td>
            </tr>
          `).join('');
        }
      }
    } catch (e) {
      console.error('Failed to load users', e);
    }
  };

  // Settings modification
  const saveSettingsBtn = document.getElementById('saveSettingsBtn');
  if (saveSettingsBtn) {
    saveSettingsBtn.addEventListener('click', async () => {
      const newName = document.getElementById('set-name').value;
      const newEmail = document.getElementById('set-email').value;
      
      try {
        const res = await fetch('/api/v1/settings', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: newName, email: newEmail })
        }).then(r => r.json());
        
        if (res.success) {
          document.querySelector('.profile-name').textContent = res.settings.name.split(' ')[0] + '.';
          document.querySelector('.user-full-name').textContent = res.settings.name;
          document.querySelector('.user-email').textContent = res.settings.email;
          document.querySelector('.sidebar-user-panel .user-name').textContent = res.settings.name;
          showToast('Settings saved to database successfully!', 'success');
        }
      } catch (e) {
        showToast('Failed to save settings.', 'danger');
      }
    });
  }

  // --- Chart color generators based on active filters ---
  const getRegionColors = (isDark) => {
    const baseColors = ['#7c3aed', '#06b6d4', '#8b5cf6', '#10b981', '#f59e0b'];
    if (!state.filters.region) return baseColors;
    const regions = ['Maharashtra', 'Gujarat', 'Karnataka', 'Telangana', 'Delhi'];
    const dimmedColor = isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.08)';
    return regions.map((r, idx) => r === state.filters.region ? baseColors[idx] : dimmedColor);
  };

  const getCustomerColors = (isDark) => {
    const primary = '#4f46e5';
    const secondary = '#06b6d4';
    const dimmedColor = isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.08)';
    if (!state.filters.segment) return [primary, secondary];
    if (state.filters.segment === 'New Clients') return [primary, dimmedColor];
    return [dimmedColor, secondary];
  };

  const getProductColors = (isDark) => {
    const baseColors = ['#4f46e5', '#8b5cf6', '#06b6d4', '#10b981'];
    if (!state.filters.product) return baseColors;
    const products = ['Apple iPhone 16', 'Apple iPhone 16 Pro', 'Samsung Galaxy S25', 'Samsung Galaxy S25 Ultra', 'OnePlus 14', 'Google Pixel 10', 'MacBook Air M4', 'MacBook Pro M4', 'Dell XPS 15', 'HP Pavilion 15', 'Lenovo ThinkBook 16', 'ASUS ROG Strix G16', 'iPad Air', 'Samsung Galaxy Tab S10', 'Apple Watch Series 11', 'Samsung Galaxy Watch 8', 'AirPods Pro 3', 'Sony WH-1000XM6', 'JBL Flip 7', 'Logitech MX Master 4'];
    const dimmedColor = isDark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.08)';
    return products.map((p, idx) => p === state.filters.product ? baseColors[idx] : dimmedColor);
  };

  // Update visual breadcrumbs and filters indicator
  const updateFiltersDisplay = () => {
    const breadcrumbsContainer = document.getElementById('drilldownBreadcrumbs');
    const filtersBar = document.getElementById('activeFiltersBar');
    
    if (!breadcrumbsContainer) return;

    const hasActiveFilters = Object.keys(state.filters).some(key => {
      if (key === 'period') return false;
      return state.filters[key] !== null;
    });
    
    if (filtersBar) {
      filtersBar.style.display = hasActiveFilters ? 'flex' : 'none';
    }

    // Update Filter Badges
    const badgeIds = ['region', 'month', 'segment', 'product'];
    badgeIds.forEach(id => {
      const badge = document.getElementById(`badge-${id}`);
      if (badge) {
        const val = state.filters[id];
        if (val) {
          badge.style.display = 'inline-flex';
          badge.querySelector('.val').textContent = val;
        } else {
          badge.style.display = 'none';
        }
      }
    });

    // Build Breadcrumbs
    breadcrumbsContainer.innerHTML = '';
    
    // Home Breadcrumb
    const homeNode = document.createElement('span');
    homeNode.className = 'breadcrumb-node' + (!hasActiveFilters ? ' active' : '');
    homeNode.textContent = 'InsightHub Overview';
    homeNode.addEventListener('click', () => {
      resetAllFilters();
    });
    breadcrumbsContainer.appendChild(homeNode);

    if (state.filters.region) {
      breadcrumbsContainer.appendChild(createSeparator());
      const regionNode = document.createElement('span');
      regionNode.className = 'breadcrumb-node' + (!state.filters.month && !state.filters.segment && !state.filters.product ? ' active' : '');
      regionNode.textContent = state.filters.region;
      regionNode.addEventListener('click', () => {
        state.filters.month = null;
        state.filters.segment = null;
        state.filters.product = null;
        state.drillLevel = 'region';
        updateDashboard();
      });
      breadcrumbsContainer.appendChild(regionNode);
    }

    if (state.filters.month) {
      breadcrumbsContainer.appendChild(createSeparator());
      const monthNode = document.createElement('span');
      monthNode.className = 'breadcrumb-node' + (!state.filters.segment && !state.filters.product ? ' active' : '');
      monthNode.textContent = state.filters.month;
      monthNode.addEventListener('click', () => {
        state.filters.segment = null;
        state.filters.product = null;
        state.drillLevel = 'month';
        updateDashboard();
      });
      breadcrumbsContainer.appendChild(monthNode);
    }

    if (state.filters.segment) {
      breadcrumbsContainer.appendChild(createSeparator());
      const segmentNode = document.createElement('span');
      segmentNode.className = 'breadcrumb-node' + (!state.filters.product ? ' active' : '');
      segmentNode.textContent = state.filters.segment;
      segmentNode.addEventListener('click', () => {
        state.filters.product = null;
        state.drillLevel = 'customer';
        updateDashboard();
      });
      breadcrumbsContainer.appendChild(segmentNode);
    }

    if (state.filters.product) {
      breadcrumbsContainer.appendChild(createSeparator());
      const productNode = document.createElement('span');
      productNode.className = 'breadcrumb-node active';
      productNode.textContent = state.filters.product;
      breadcrumbsContainer.appendChild(productNode);
    }
  };

  const createSeparator = () => {
    const span = document.createElement('span');
    span.className = 'breadcrumb-separator';
    span.textContent = ' > ';
    return span;
  };

  // =====================================================================
  // AI INSIGHTS PAGE — Full Rendering Engine
  // =====================================================================
  let currentAiData = null;
  
  const AI_INSIGHT_COLORS = {
    revenue: '#4f46e5',
    customer: '#06b6d4',
    product: '#10b981',
    risk: '#f59e0b'
  };
  const AI_INSIGHT_GLOWS = {
    revenue: 'rgba(79,70,229,0.12)',
    customer: 'rgba(6,182,212,0.12)',
    product: 'rgba(16,185,129,0.12)',
    risk: 'rgba(245,158,11,0.12)'
  };
  const AI_INSIGHT_ICONS = {
    revenue: '\uD83D\uDCC8',
    customer: '\uD83D\uDC65',
    product: '\uD83D\uDCE6',
    risk: '\uD83D\uDEE1\uFE0F'
  };

  // Render sparkline inside a container element
  const renderSparkline = (containerId, data, color) => {
    const el = document.getElementById(containerId);
    if (!el || !window.ApexCharts) return;
    el.innerHTML = '';
    const spark = new ApexCharts(el, {
      chart: { type: 'line', height: 36, sparkline: { enabled: true }, background: 'transparent' },
      series: [{ data }],
      stroke: { curve: 'smooth', width: 2 },
      colors: [color],
      tooltip: { enabled: false }
    });
    spark.render();
  };

  // Render AI KPI cards
  const renderAiKpiCards = (data) => {
    const grid = document.getElementById('aiKpiGrid');
    if (!grid) return;
    const kpis = [
      {
        id: 'ai-kpi-accuracy', label: 'Forecast Accuracy', value: data.kpis.forecastAccuracy.toFixed(1) + '%',
        trend: '+2.1%', trendDir: 'up', color: '#4f46e5', glow: 'rgba(79,70,229,0.12)',
        icon: '\uD83C\uDFAF', sparkData: data.sparklines.revenue, sparkId: 'spark-accuracy'
      },
      {
        id: 'ai-kpi-growth', label: 'Revenue Growth Prediction', value: '+' + data.kpis.revenuePrediction.toFixed(1) + '%',
        trend: 'vs prev period', trendDir: 'up', color: '#10b981', glow: 'rgba(16,185,129,0.12)',
        icon: '\uD83D\uDCC8', sparkData: data.sparklines.growth, sparkId: 'spark-growth'
      },
      {
        id: 'ai-kpi-risk', label: 'Business Risk Score', value: data.kpis.riskScore + '/100',
        trend: data.kpis.riskLevel + ' Risk', trendDir: data.kpis.riskScore < 30 ? 'up' : (data.kpis.riskScore < 60 ? 'neutral' : 'down'),
        color: '#f59e0b', glow: 'rgba(245,158,11,0.12)',
        icon: '\u26A0\uFE0F', sparkData: data.sparklines.risk, sparkId: 'spark-risk'
      },
      {
        id: 'ai-kpi-nps', label: 'Customer Satisfaction', value: Math.round(data.kpis.satisfactionScore),
        trend: 'NPS Score', trendDir: 'up', color: '#06b6d4', glow: 'rgba(6,182,212,0.12)',
        icon: '\uD83D\uDE0A', sparkData: data.sparklines.nps, sparkId: 'spark-nps'
      }
    ];
    grid.innerHTML = kpis.map(k => `
      <div class="ai-kpi-card" style="--ai-card-color:${k.color}; --ai-card-glow:${k.glow};" id="${k.id}">
        <div class="ai-kpi-card-top">
          <div class="ai-kpi-icon-wrap">${k.icon}</div>
          <div class="ai-kpi-trend-badge ${k.trendDir}">${k.trendDir === 'up' ? '&#9650;' : k.trendDir === 'down' ? '&#9660;' : '&#9658;'} ${k.trend}</div>
        </div>
        <div class="ai-kpi-value">${k.value}</div>
        <div class="ai-kpi-label">${k.label}</div>
        <div class="ai-kpi-sparkline" id="${k.sparkId}"></div>
      </div>
    `).join('');
    // Render sparklines after DOM update
    setTimeout(() => {
      kpis.forEach(k => renderSparkline(k.sparkId, k.sparkData, k.color));
    }, 50);
  };

  // Render forecast confidence chart from API data
  const renderAiForecastChart = (data, isDarkMode) => {
    const el = document.getElementById('aiConfidenceChart');
    if (!el) return;
    el.innerHTML = '';
    const textColor = isDarkMode ? '#94a3b8' : '#64748b';
    const gridColor = isDarkMode ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)';

    if (chartInstances.aiConfidence) {
      try { chartInstances.aiConfidence.destroy(); } catch(e) {}
    }

    const options = {
      chart: {
        type: 'line', height: 300, toolbar: { show: false }, background: 'transparent',
        animations: { enabled: true, easing: 'easeinout', speed: 800 }
      },
      series: [
        {
          name: 'Actual Revenue',
          type: 'area',
          data: data.forecast.actualSeries.map((v, i) => i < 6 ? (v || null) : null)
        },
        {
          name: 'AI Forecast',
          type: 'line',
          data: data.forecast.forecastSeries
        }
      ],
      colors: ['#4f46e5', '#10b981'],
      stroke: {
        curve: ['smooth', 'smooth'],
        width: [2, 2],
        dashArray: [0, 6]
      },
      fill: {
        type: ['gradient', 'solid'],
        gradient: { shade: 'dark', type: 'vertical', opacityFrom: 0.25, opacityTo: 0.02, stops: [0, 100] }
      },
      markers: { size: [3, 4], strokeWidth: 0 },
      xaxis: {
        categories: data.forecast.categories,
        labels: { style: { colors: textColor, fontSize: '0.7rem' } },
        axisBorder: { show: false }, axisTicks: { show: false }
      },
      yaxis: {
        labels: {
          style: { colors: textColor, fontSize: '0.7rem' },
          formatter: v => {
            if (!v || v === 0) return '0';
            if (v >= 10000000) return '\u20b9' + (v/10000000).toFixed(1) + 'Cr';
            if (v >= 100000) return '\u20b9' + (v/100000).toFixed(0) + 'L';
            return '\u20b9' + Math.round(v/1000) + 'K';
          }
        }
      },
      grid: { borderColor: gridColor, strokeDashArray: 4 },
      tooltip: {
        theme: isDarkMode ? 'dark' : 'light',
        y: {
          formatter: v => {
            if (!v || v === 0) return 'No data';
            const n = Math.round(v);
            const s = String(n);
            if (s.length <= 3) return '\u20b9' + s;
            const l3 = s.slice(-3), rest = s.slice(0, -3);
            const groups = [];
            let r = rest;
            while (r.length > 2) { groups.unshift(r.slice(-2)); r = r.slice(0, -2); }
            if (r) groups.unshift(r);
            return '\u20b9' + groups.join(',') + ',' + l3;
          }
        }
      },
      legend: {
        show: true, position: 'top', horizontalAlign: 'right',
        labels: { colors: textColor }, markers: { radius: 3 }
      },
      theme: { mode: isDarkMode ? 'dark' : 'light' }
    };

    chartInstances.aiConfidence = new ApexCharts(el, options);
    chartInstances.aiConfidence.render();

    // Update explanation
    const expEl = document.getElementById('aiForecastExplanation');
    if (expEl) {
      expEl.innerHTML = '<strong>Model Explanation:</strong> ' + (data.forecast.explanation || 'Forecast data loaded from database.');
    }
  };

  // Render predictive analytics summary card
  const renderAiPredictiveCard = (data) => {
    const card = document.getElementById('aiPredictiveCard');
    if (!card) return;
    const metrics = [
      { icon: '\uD83C\uDFC6', color: '#4f46e5', glow: 'rgba(79,70,229,0.12)', label: 'Top Growth Region', value: data.predictive.topRegion, sub: data.predictive.topRegionRevenue + ' revenue' },
      { icon: '\uD83D\uDCE6', color: '#10b981', glow: 'rgba(16,185,129,0.12)', label: 'Top Performing Product', value: data.predictive.topProduct, sub: data.predictive.topProductRevenue + ' revenue' },
      { icon: '\uD83D\uDC65', color: '#06b6d4', glow: 'rgba(6,182,212,0.12)', label: 'Fastest Growing Segment', value: data.predictive.topSegment, sub: 'Primary customer driver' },
      { icon: '\uD83D\uDCC9', color: '#f59e0b', glow: 'rgba(245,158,11,0.12)', label: 'Revenue Trend', value: data.predictive.trend === 'upward' ? '\u2197\uFE0F Upward' : '\u2198\uFE0F Downward', sub: 'Profit margin: ' + data.predictive.profitMargin + '%' },
      { icon: '\uD83D\uDCB0', color: '#8b5cf6', glow: 'rgba(139,92,246,0.12)', label: 'Total Portfolio Revenue', value: data.predictive.totalRevenue, sub: 'Across all active transactions' }
    ];

    // Rebuild card keeping the h3 header
    const h3 = card.querySelector('h3');
    const h3Html = h3 ? h3.outerHTML : '';
    card.innerHTML = h3Html + metrics.map(m => `
      <div class="ai-predictive-metric">
        <div class="ai-predictive-metric-icon" style="background:${m.glow};">${m.icon}</div>
        <div class="ai-predictive-metric-body">
          <div class="ai-predictive-metric-label">${m.label}</div>
          <div class="ai-predictive-metric-value">${m.value}</div>
          <div class="ai-predictive-metric-sub">${m.sub}</div>
        </div>
      </div>
    `).join('');
  };

  // Render AI insight cards
  const renderAiInsightCards = (insights) => {
    const grid = document.getElementById('aiInsightCardsGrid');
    if (!grid) return;
    grid.innerHTML = insights.map((ins, idx) => {
      const color = AI_INSIGHT_COLORS[ins.type] || '#4f46e5';
      const glow = AI_INSIGHT_GLOWS[ins.type] || 'rgba(79,70,229,0.12)';
      const icon = AI_INSIGHT_ICONS[ins.type] || '\uD83D\uDCA1';
      return `
      <div class="ai-insight-card-new" style="--insight-color:${color};" data-insight-idx="${idx}">
        <div class="ai-insight-card-header">
          <div class="ai-insight-card-icon" style="background:${glow}; font-size:1.2rem;">${icon}</div>
          <div class="ai-insight-card-title">${ins.title}</div>
          <div class="ai-insight-card-type-badge" style="background:${glow}; color:${color};">${ins.type.toUpperCase()}</div>
        </div>
        <div class="ai-insight-finding">${ins.finding}</div>
        <div class="ai-confidence-row">
          <div class="ai-confidence-label">Model Confidence</div>
          <div class="ai-confidence-pct">${ins.confidence}%</div>
        </div>
        <div class="ai-confidence-bar-track">
          <div class="ai-confidence-bar-fill" style="width:0%;" data-target="${ins.confidence}%"></div>
        </div>
        <div class="ai-insight-action-row">
          <div class="ai-insight-action-text">${ins.action}</div>
          <button class="ai-insight-detail-btn" data-insight-idx="${idx}">
            Details &#8594;
          </button>
        </div>
      </div>
    `;
    }).join('');

    // Animate confidence bars
    setTimeout(() => {
      document.querySelectorAll('.ai-confidence-bar-fill[data-target]').forEach(bar => {
        bar.style.width = bar.getAttribute('data-target');
      });
    }, 100);

    // Bind detail button clicks
    document.querySelectorAll('[data-insight-idx]').forEach(el => {
      el.addEventListener('click', (e) => {
        const idx = parseInt(el.getAttribute('data-insight-idx'));
        if (!isNaN(idx) && currentAiData && currentAiData.insights[idx]) {
          openAiInsightModal(currentAiData.insights[idx]);
        }
      });
    });
  };

  // Render executive report card
  const renderAiExecutiveReport = (data) => {
    const card = document.getElementById('aiExecutiveReport');
    if (!card) return;
    const h3 = card.querySelector('h3');
    const h3Html = h3 ? h3.outerHTML : '';
    const riskClass = (data.riskAnalysis.riskLevel || 'Low').toLowerCase();
    const growthSign = data.forecast.predictedGrowth >= 0 ? '+' : '';

    card.innerHTML = h3Html + `
      <div class="ai-report-section-block">
        <div class="ai-report-section-title">
          <span>&#128200;</span> Revenue Forecast
        </div>
        <div class="ai-report-metric-row">
          <span class="ai-report-metric-key">Projected Next Period Revenue</span>
          <span class="ai-report-metric-val">${data.forecast.nextMonthRevenueFormatted}</span>
        </div>
        <div class="ai-report-metric-row">
          <span class="ai-report-metric-key">Expected Growth</span>
          <span class="ai-report-metric-val" style="color:var(--success);">${growthSign}${data.forecast.predictedGrowth.toFixed(1)}%</span>
        </div>
        <div class="ai-report-metric-row">
          <span class="ai-report-metric-key">Forecast Confidence</span>
          <span class="ai-report-metric-val">${data.forecast.confidenceAccuracy}%</span>
        </div>
      </div>
      <div class="ai-report-section-block">
        <div class="ai-report-section-title">
          <span>&#9888;&#65039;</span> Risk Analysis
        </div>
        <div class="ai-report-metric-row">
          <span class="ai-report-metric-key">Business Risk Level</span>
          <span class="ai-report-risk-badge ${riskClass}">${data.riskAnalysis.riskLevel} Risk</span>
        </div>
        <div class="ai-report-metric-row">
          <span class="ai-report-metric-key">Pending Transactions</span>
          <span class="ai-report-metric-val">${data.riskAnalysis.pendingOrders} orders</span>
        </div>
        <div class="ai-report-metric-row">
          <span class="ai-report-metric-key">UPI Infrastructure</span>
          <span class="ai-report-metric-val">${data.riskAnalysis.upiHealth}</span>
        </div>
        <div class="ai-report-metric-row">
          <span class="ai-report-metric-key">Active Alerts</span>
          <span class="ai-report-metric-val">${data.riskAnalysis.alertCount}</span>
        </div>
      </div>
    `;
  };

  // Render recommendations card
  const renderAiRecommendations = (recommendations) => {
    const card = document.getElementById('aiRecommendationsCard');
    if (!card) return;
    const h3 = card.querySelector('h3');
    const h3Html = h3 ? h3.outerHTML : '';
    card.innerHTML = h3Html + recommendations.map(r => `
      <div class="ai-rec-item">
        <div class="ai-rec-priority ${r.priority.toLowerCase()}">${r.priority}</div>
        <div class="ai-rec-body">
          <div class="ai-rec-action">${r.action}</div>
          <div class="ai-rec-impact">&#128200; ${r.expectedImpact}</div>
        </div>
      </div>
    `).join('');
  };

  // Open AI insight modal
  const openAiInsightModal = (insight) => {
    const modal = document.getElementById('aiInsightModal');
    const iconEl = document.getElementById('aiModalIcon');
    const titleEl = document.getElementById('aiModalTitle');
    const subtitleEl = document.getElementById('aiModalSubtitle');
    const findingEl = document.getElementById('aiModalFinding');
    const metricsEl = document.getElementById('aiModalMetricsGrid');
    const actionEl = document.getElementById('aiModalAction');
    if (!modal) return;

    const color = AI_INSIGHT_COLORS[insight.type] || '#4f46e5';
    const glow = AI_INSIGHT_GLOWS[insight.type] || 'rgba(79,70,229,0.12)';
    const icon = AI_INSIGHT_ICONS[insight.type] || '&#128161;';

    modal.style.setProperty('--modal-color', color);
    if (iconEl) {
      iconEl.style.background = glow;
      iconEl.style.fontSize = '1.5rem';
      iconEl.innerHTML = icon;
    }
    if (titleEl) titleEl.textContent = insight.title;
    if (subtitleEl) subtitleEl.textContent = 'Supporting metrics & AI analysis';
    if (findingEl) findingEl.textContent = insight.finding;
    if (metricsEl && insight.supportingMetrics) {
      metricsEl.innerHTML = Object.entries(insight.supportingMetrics).map(([k, v]) => `
        <div class="ai-modal-metric-card">
          <div class="ai-modal-metric-card-label">${k}</div>
          <div class="ai-modal-metric-card-value">${v}</div>
        </div>
      `).join('');
    }
    if (actionEl) actionEl.textContent = insight.action;

    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
  };

  const closeAiInsightModal = () => {
    const modal = document.getElementById('aiInsightModal');
    if (modal) modal.classList.remove('active');
    document.body.style.overflow = '';
  };

  // Main AI Insights page renderer
  const updateAiInsights = async () => {
    try {
      const aiPeriod = (document.getElementById('aiPeriodFilter') || {}).value || state.filters.period || 'yearly';
      const queryStr = buildQueryString({ period: aiPeriod });
      const data = await fetch(`/api/v1/ai-insights${queryStr}`).then(r => r.json());
      if (data.error) throw new Error(data.error);

      currentAiData = data;
      const isDarkMode = document.documentElement.getAttribute('data-theme') !== 'light';

      renderAiKpiCards(data);
      renderAiForecastChart(data, isDarkMode);
      renderAiPredictiveCard(data);
      renderAiInsightCards(data.insights);
      renderAiExecutiveReport(data);
      renderAiRecommendations(data.recommendations);
      renderExecutiveReports();


      // Also update the dashboard-level AI insight elements (if they exist)
      const revenueEl = document.getElementById('ai-insight-revenue');
      const customersEl = document.getElementById('ai-insight-customers');
      const salesEl = document.getElementById('ai-insight-sales');
      const recommendationsEl = document.getElementById('ai-insight-recommendations');
      if (data.insights[0] && revenueEl) revenueEl.innerHTML = data.insights[0].finding;
      if (data.insights[1] && customersEl) customersEl.innerHTML = data.insights[1].finding;
      if (data.insights[2] && salesEl) salesEl.innerHTML = data.insights[2].finding;
      if (data.insights[3] && recommendationsEl) recommendationsEl.innerHTML = data.insights[3].action;
    } catch (e) {
      console.error("Failed to load AI Insights", e);
    }
  };

  // Modal close bindings
  const aiModalCloseBtn = document.getElementById('aiModalClose');
  if (aiModalCloseBtn) aiModalCloseBtn.addEventListener('click', closeAiInsightModal);
  const aiModalOverlay = document.getElementById('aiInsightModal');
  if (aiModalOverlay) {
    aiModalOverlay.addEventListener('click', (e) => {
      if (e.target === aiModalOverlay) closeAiInsightModal();
    });
  }
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeAiInsightModal();
  });

  // AI period filter change
  const aiPeriodFilter = document.getElementById('aiPeriodFilter');
  if (aiPeriodFilter) {
    aiPeriodFilter.addEventListener('change', () => {
      updateAiInsights();
    });
  }

  // AI refresh button
  const aiRefreshBtn = document.getElementById('aiRefreshBtn');
  if (aiRefreshBtn) {
    aiRefreshBtn.addEventListener('click', () => {
      aiRefreshBtn.disabled = true;
      aiRefreshBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="animation:spin 1s linear infinite"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg> Refreshing...`;
      updateAiInsights().finally(() => {
        aiRefreshBtn.disabled = false;
        aiRefreshBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg> Refresh Analysis`;
      });
    });
  }

  // Core Async Dashboard Refresh function
  const updateDashboard = async (isFilterOrManualChange = true) => {
    try {
      const queryStr = buildQueryString();
      
      // 1. Fetch metrics & update counters
      const metrics = await fetch(`/api/v1/metrics${queryStr}`).then(r => r.json());
      
      const prevMetrics = state.latestMetrics || {};
      
      const hasChanged = !prevMetrics.revenue || 
                         prevMetrics.revenue !== metrics.revenue ||
                         prevMetrics.sales !== metrics.sales ||
                         prevMetrics.customers !== metrics.customers ||
                         prevMetrics.orders !== metrics.orders ||
                         prevMetrics.profit !== metrics.profit ||
                         prevMetrics.growth !== metrics.growth ||
                         prevMetrics.nps !== metrics.nps ||
                         prevMetrics.npsChange !== metrics.npsChange;
      
      state.latestMetrics = metrics;

      // Update new Dashboard Core Metrics
      const tpEl = document.getElementById('metric-top-product');
      const tpuEl = document.getElementById('metric-top-units');
      const aovEl = document.getElementById('metric-aov');
      const compEl = document.getElementById('metric-completed');
      const pendEl = document.getElementById('metric-pending');
      
      if (tpEl) tpEl.textContent = metrics.topProduct || 'N/A';
      if (tpuEl) tpuEl.textContent = `${(metrics.topProductUnits || 0).toLocaleString('en-IN')} units`;
      if (aovEl) aovEl.textContent = formatIndianRupees(metrics.aov || 0);
      if (compEl) compEl.textContent = (metrics.completedOrders || 0).toLocaleString('en-IN');
      if (pendEl) pendEl.textContent = (metrics.pendingOrders || 0).toLocaleString('en-IN');

      // Update AI Health Score
      const healthCont = document.getElementById('health-score-container');
      const healthValEl = document.getElementById('dynamic-health-score');
      if (healthCont && healthValEl) {
        if (metrics.healthScore === null || metrics.healthScore === undefined) {
          healthCont.innerHTML = `<span style="font-size: 1.2rem; color: var(--text-secondary);">Insufficient data for AI health analysis</span>`;
          // Clear gauge if it exists
          const gauge = document.getElementById('healthGaugeContainer');
          if (gauge) gauge.innerHTML = '';
        } else {
          // Restore container if it was previously set to insufficient data
          if (!healthCont.querySelector('.score-max')) {
            healthCont.innerHTML = `<span class="score-num"><span id="dynamic-health-score">${metrics.healthScore}</span><span class="score-max">/100</span></span>
                <p class="score-desc">Calculated based on Revenue Growth, Completed Order Percentage, Customer Growth, Profit Margin, and Pending Order Ratio.</p>`;
          } else {
            document.getElementById('dynamic-health-score').textContent = metrics.healthScore;
          }
          
          // ApexChart handles the gauge rendering in renderAllCharts()
        }
      }

      // Update NPS text elements immediately
      const npsScoreEl = document.getElementById('npsScoreVal');
      const npsTrendEl = document.getElementById('npsTrendVal');
      if (npsScoreEl) npsScoreEl.textContent = metrics.nps.toFixed(0);
      if (npsTrendEl) {
        const change = metrics.npsChange;
        if (change > 0) {
          npsTrendEl.innerHTML = `&#9650; Positive (+${change.toFixed(1)}%)`;
          npsTrendEl.className = 'text-success';
        } else if (change < 0) {
          npsTrendEl.innerHTML = `&#9660; Negative (${change.toFixed(1)}%)`;
          npsTrendEl.className = 'text-danger';
        } else {
          npsTrendEl.innerHTML = `&#9632; Stable (0.0%)`;
          npsTrendEl.className = 'text-warning';
        }
      }

      if (isFilterOrManualChange || hasChanged) {
        triggerKpiAnimations();
        
        // 2. Fetch and render orders table
        const orders = await fetch(`/api/v1/orders${queryStr}`).then(r => r.json());
        renderOrdersTable(orders.data || orders);

        // 3. Render charts
        await renderAllCharts();

        // 4. Update activities timeline & alerts
        await populateTimeline();
        await populateAlertsCenter();

        // 5. Update AI insights & filter tags display
        await updateAiInsights();
        updateFiltersDisplay();
      } else {
        // Just set values directly without restart animation
        if (kpiRev) kpiRev.textContent = formatIndianRupees(metrics.revenue);
        if (kpiSales) kpiSales.textContent = metrics.sales.toLocaleString('en-IN');
        if (kpiCust) kpiCust.textContent = metrics.customers.toLocaleString('en-IN');
        if (kpiOrd) kpiOrd.textContent = metrics.orders.toLocaleString('en-IN');
        if (kpiProf) kpiProf.textContent = metrics.profit.toFixed(1) + '%';
        if (kpiGrow) kpiGrow.textContent = metrics.growth.toFixed(1) + '%';
        
        // Update NPS chart series silently
        if (chartInstances.nps) {
          chartInstances.nps.updateSeries([Math.round(metrics.nps)]);
        }
      }

      // Update secondary KPIs (GST & UPI estimate cards)
      const gstEl = document.getElementById('metric-gst');
      if (gstEl) {
        gstEl.textContent = formatIndianRupees(metrics.revenue * 0.18);
      }
      const upiEl = document.getElementById('metric-upi');
      if (upiEl) {
        upiEl.textContent = Math.floor(metrics.orders * 0.62).toLocaleString('en-IN');
      }

      // Update the Last Updated timestamp in the header
      const now = new Date();
      const timestampStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      const lastUpdatedBadge = document.getElementById('lastUpdatedBadge');
      if (lastUpdatedBadge) {
        lastUpdatedBadge.textContent = `Refreshed: ${timestampStr}`;
      }

    } catch (e) {
      console.error("Dashboard refresh error", e);
    }
  };

  const resetAllFilters = () => {
    state.filters.region = null;
    state.filters.month = null;
    state.filters.segment = null;
    state.filters.product = null;
    state.filters.period = 'monthly';
    state.drillLevel = 'dashboard';
    
    ['filter-sales', 'filter-region', 'filter-customers', 'filter-profit'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.value = 'monthly';
    });

    updateDashboard();
    showToast('Reset all filters to overall view.', 'info');
  };

  // Bind Active Filter Badge Remove Listeners
  document.querySelectorAll('.filter-badge .remove').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const filterType = btn.getAttribute('data-filter');
      if (filterType) {
        state.filters[filterType] = null;
        updateDashboard();
        showToast(`Cleared ${filterType} filter.`, 'info');
      }
    });
  });

  // Bind Global Reset Button
  const resetBtn = document.getElementById('resetFiltersBtn');
  if (resetBtn) {
    resetBtn.addEventListener('click', resetAllFilters);
  }

  // --- Update currentDate text node (DD/MM/YYYY) ---
  const today = new Date();
  const day = String(today.getDate()).padStart(2, '0');
  const month = String(today.getMonth() + 1).padStart(2, '0');
  const year = today.getFullYear();
  const dateEl = document.getElementById('currentDate');
  if (dateEl) dateEl.textContent = `${day}/${month}/${year}`;

  // --- Chart Time Filter Event Listeners with Skeleton Refresh ---
  ['filter-sales', 'filter-region', 'filter-customers', 'filter-profit'].forEach(id => {
    const selectEl = document.getElementById(id);
    if (selectEl) {
      selectEl.addEventListener('change', () => {
        const val = selectEl.value;
        state.filters.period = val;

        // Sync all other selectors to the same period
        ['filter-sales', 'filter-region', 'filter-customers', 'filter-profit'].forEach(otherId => {
          const otherSelect = document.getElementById(otherId);
          if (otherSelect && otherSelect.value !== val) {
            otherSelect.value = val;
          }
        });

        let containerSelector = '';
        if (id === 'filter-sales') containerSelector = '#salesTrendChartContainer';
        else if (id === 'filter-region') containerSelector = '#revenueRegionChartContainer';
        else if (id === 'filter-customers') containerSelector = '#customerGrowthChartContainer';
        else if (id === 'filter-profit') containerSelector = '#profitAnalysisChartContainer';

        const container = document.querySelector(containerSelector);
        if (container) {
          const parentCard = container.closest('.chart-card');
          if (parentCard) {
            parentCard.style.position = 'relative';
            const skeleton = document.createElement('div');
            skeleton.className = 'skeleton-overlay';
            skeleton.innerHTML = `
              <div class="skeleton-line short"></div>
              <div class="skeleton-line medium" style="margin-top: 10px;"></div>
              <div class="skeleton-line tall" style="margin-top: 15px; height: 160px;"></div>
            `;
            parentCard.appendChild(skeleton);
            setTimeout(() => {
              skeleton.remove();
              updateDashboard();
            }, 600);
          } else {
            updateDashboard();
          }
        } else {
          updateDashboard();
        }

        showToast(`Filtered dashboard by period: ${val.toUpperCase()}`, 'success');
      });
    }
  });

  // --- AI Health Score Card Click Event ---
  const healthCard = document.querySelector('.health-score-card');
  if (healthCard) {
    healthCard.addEventListener('click', () => {
      const htmlContent = `
        <div style="font-family: var(--font-family); line-height: 1.6;">
          <h4 style="margin-bottom: 12px; font-weight: 800; font-size: 1.15rem;">AI Business Health Score Breakdown</h4>
          <p style="color: var(--text-secondary); margin-bottom: 16px;">
            The overall health index of <strong>92/100</strong> is computed across 14 financial and performance pipeline indicators:
          </p>
          <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
            <tr style="border-bottom: 1px solid var(--sidebar-border);">
              <td style="padding: 8px 0; color: var(--text-secondary); font-weight: 600;">Financial Health Rating:</td>
              <td style="padding: 8px 0; font-weight: 700; text-align: right; color: var(--success);">94% (Excellent)</td>
            </tr>
            <tr style="border-bottom: 1px solid var(--sidebar-border);">
              <td style="padding: 8px 0; color: var(--text-secondary); font-weight: 600;">Transaction Failure Rate:</td>
              <td style="padding: 8px 0; font-weight: 700; text-align: right; color: var(--success);">0.12% (Negligible)</td>
            </tr>
            <tr style="border-bottom: 1px solid var(--sidebar-border);">
              <td style="padding: 8px 0; color: var(--text-secondary); font-weight: 600;">API Endpoint Latency:</td>
              <td style="padding: 8px 0; font-weight: 700; text-align: right; color: var(--success);">142ms (Healthy)</td>
            </tr>
            <tr style="border-bottom: 1px solid var(--sidebar-border);">
              <td style="padding: 8px 0; color: var(--text-secondary); font-weight: 600;">UPI Retry Loop Success:</td>
              <td style="padding: 8px 0; font-weight: 700; text-align: right; color: var(--success);">98.8%</td>
            </tr>
            <tr style="border-bottom: 1px solid var(--sidebar-border);">
              <td style="padding: 8px 0; color: var(--text-secondary); font-weight: 600;">Customer Churn Hazard Ratio:</td>
              <td style="padding: 8px 0; font-weight: 700; text-align: right; color: var(--secondary);">0.08 (Low Risk)</td>
            </tr>
            <tr style="border-bottom: 1px solid var(--sidebar-border);">
              <td style="padding: 8px 0; color: var(--text-secondary); font-weight: 600;">Active Vendor Reliability:</td>
              <td style="padding: 8px 0; font-weight: 700; text-align: right; color: var(--success);">99.4%</td>
            </tr>
          </table>
          <div style="background: rgba(79, 70, 229, 0.05); border: 1px solid rgba(79, 70, 229, 0.2); padding: 14px; border-radius: 12px; margin-bottom: 20px;">
            <h4 style="font-weight: 700; font-size: 0.85rem; text-transform: uppercase; color: var(--primary); margin-bottom: 8px;">Automated Strategic Guidelines:</h4>
            <p style="font-size: 0.82rem; color: var(--text-secondary); margin-bottom: 0;">
              • Redirect surplus UPI marketing capital into Western Maharashtra B2B cloud tokens.
              <br/>• Maintain Apple iPhone 16 reserve counts above critical margins.
              <br/>• Optimize Razorpay gateway webhook endpoints to decrease current retry loop delay.
            </p>
          </div>
          <div style="display: flex; gap: 12px; justify-content: flex-end;">
            <button class="btn btn-secondary" onclick="document.getElementById('modalCloseBtn').click()">Close Breakdown</button>
            <button class="btn btn-primary" onclick="showToast('Strategic report queued for export.', 'success'); document.getElementById('modalCloseBtn').click()">Export Report</button>
          </div>
        </div>
      `;
      openModal('AI Health Score Diagnostics', htmlContent);
    });
  }

  
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


  // --- Profile Dropdown Actions ---
  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', async (e) => {
      e.preventDefault();
      showToast('Signing out...', 'info');
      try {
        await fetch('/api/v1/logout', { method: 'POST' });
        window.location.href = '/login';
      } catch (err) {
        window.location.href = '/login';
      }
    });
  }
// --- Real-time 5-Second Auto-Refresh Loop ---
  const runAutoRefresh = () => {
    // Only invoke refresh if dashboard or active views are open
    updateDashboard(false);
  };

  
  // --- Data Management Logic ---
      
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
        date: document.getElementById('orderDate').value.split('-').reverse().join('/')
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
          loadProducts();
          filterOrdersTable();
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
            loadProducts();
            filterOrdersTable();
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

  // Orders Management Event Listeners
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
    const csvContent = "Customer Name,Product,Amount,Region,Status,Date\nJohn Doe,Apple iPhone 16,150000.00,Maharashtra,Delivered,15/08/2026\nJane Smith,MacBook Air M4,250000.00,Karnataka,Processing,16/08/2026";
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

  const loadProducts = async () => {
    try {
      const res = await fetch('/api/v1/products');
      if (res.ok) {
        const products = await res.json();
        
        const orderProductSelect = document.getElementById('orderProduct');
        const orderProductFilterSelect = document.getElementById('orderProductFilter');
        
        // Preserve selections
        const currentFilterVal = orderProductFilterSelect ? orderProductFilterSelect.value : 'all';
        const currentProductVal = orderProductSelect ? orderProductSelect.value : '';
        
        if (orderProductSelect) {
          orderProductSelect.innerHTML = products.map(p => `
            <option value="${p}">${p}</option>
          `).join('');
          
          if (currentProductVal && products.includes(currentProductVal)) {
            orderProductSelect.value = currentProductVal;
          }
          // Trigger autofill of amount
          orderProductSelect.dispatchEvent(new Event('change'));
        }
        
        if (orderProductFilterSelect) {
          orderProductFilterSelect.innerHTML = `
            <option value="all">All Products</option>
            ${products.map(p => `<option value="${p}">${p}</option>`).join('')}
          `;
          
          if (currentFilterVal && (currentFilterVal === 'all' || products.includes(currentFilterVal))) {
            orderProductFilterSelect.value = currentFilterVal;
          } else {
            orderProductFilterSelect.value = 'all';
          }
        }
      }
    } catch (e) {
      console.error("Failed to load products", e);
    }
  };

  // --- Initializing App ---
  loadProfileSettings();
  loadUserManagement();
  loadProducts();
  updateDashboard();
  setInterval(runAutoRefresh, 5000);
});

// Auto-fill amount based on product selection
document.addEventListener('DOMContentLoaded', () => {
  const productPrices = {
    'Apple iPhone 16': 79900,
    'Apple iPhone 16 Pro': 119900,
    'Samsung Galaxy S25': 74999,
    'Samsung Galaxy S25 Ultra': 129999,
    'OnePlus 14': 64999,
    'Google Pixel 10': 79999,
    'MacBook Air M4': 114900,
    'MacBook Pro M4': 169900,
    'Dell XPS 15': 185000,
    'HP Pavilion 15': 65000,
    'Lenovo ThinkBook 16': 75000,
    'ASUS ROG Strix G16': 145000,
    'iPad Air': 59900,
    'Samsung Galaxy Tab S10': 89999,
    'Apple Watch Series 11': 41900,
    'Samsung Galaxy Watch 8': 34999,
    'AirPods Pro 3': 24900,
    'Sony WH-1000XM6': 29990,
    'JBL Flip 7': 11999,
    'Logitech MX Master 4': 10995
  };

  const productSelect = document.getElementById('orderProduct');
  const amountInput = document.getElementById('orderAmount');

  if (productSelect && amountInput) {
    productSelect.addEventListener('change', (e) => {
      const selectedProduct = e.target.value;
      if (productPrices[selectedProduct]) {
        amountInput.value = productPrices[selectedProduct];
      } else {
        amountInput.value = '';
      }
    });

    // Trigger change initially to set the default value
    productSelect.dispatchEvent(new Event('change'));
  }
});

// --- Dynamic Dashboard Core Metrics Filtering ---
const filterByTopProduct = () => {
  const tpEl = document.getElementById('metric-top-product');
  if (tpEl && tpEl.textContent !== 'Loading...' && tpEl.textContent !== 'N/A') {
    state.filters.product = tpEl.textContent;
    updateDashboard();
    showToast(`Filtered by Top Product: ${tpEl.textContent}`, 'success');
  }
};

const filterByStatus = (status) => {
  state.filters.status = status;
  updateDashboard();
  showToast(`Filtered by Status: ${status}`, 'success');
};
