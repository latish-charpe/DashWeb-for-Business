with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the SVG hack from updateDashboard
import re
svg_hack_pattern = r"// Draw a simple circular gauge using SVG if healthGaugeContainer is empty[\s\S]*?</svg>;"

content = re.sub(svg_hack_pattern, "// ApexChart will handle the gauge rendering inside renderAllCharts", content)

# Update the ApexChart in renderAllCharts
old_apex_block = """    // 5. System Health KPI Gauge (Radial Bar)
    try {
      const healthContainer = document.querySelector("#healthGaugeContainer");
      if (healthContainer) {
        healthContainer.innerHTML = "";
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
                  formatter: val => ${val}%
                }
              },
              track: {
                background: gridColor
              }
            }
          },
          colors: ['#10b981'],
          series: [92],
          theme: { mode: isDark ? 'dark' : 'light' }
        };
        chartInstances.healthGauge = new ApexCharts(healthContainer, healthOptions);
        chartInstances.healthGauge.render();
      }
    } catch (e) {
      console.error("Error rendering health gauge", e);
    }"""

new_apex_block = """    // 5. System Health KPI Gauge (Radial Bar)
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
                  formatter: val => ${val}
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
    }"""

content = content.replace(old_apex_block, new_apex_block)

# Fix backtick formatter which Python/Powershell might ruin. We'll use replace in Python directly to be safe.
content = content.replace('formatter: val => ${val}', 'formatter: val => ${val}') # It works fine in Python string.

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(content)
