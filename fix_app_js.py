with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    "product: null       // 'Core Cloud Suite', 'CRM Enterprise', etc.",
    "product: null       // 'Apple iPhone 16', 'Samsung Galaxy S25', etc."
)

old_label_check = '''                const label = config.w.globals.labels[config.dataPointIndex];
                let productName = label;
                if (label === 'CRM Enterprise Subscriptions') productName = 'CRM Enterprise';
                state.filters.product = productName;'''
new_label_check = '''                const label = config.w.globals.labels[config.dataPointIndex];
                let productName = label;
                state.filters.product = productName;'''

content = content.replace(old_label_check, new_label_check)

old_categories = '''          xaxis: {
            categories: ['Core Cloud Suite', 'CRM Enterprise Subscriptions', 'ThreatShield Guard', 'Integration Connect'],
            labels: { style: { colors: textLabelColor } }
          },'''
new_categories = '''          xaxis: {
            categories: ['Apple iPhone 16', 'MacBook Air M4', 'Samsung Galaxy S25', 'Dell XPS 15'],
            labels: { style: { colors: textLabelColor } }
          },'''

content = content.replace(old_categories, new_categories)

old_products_array = "const products = ['Core Cloud Suite', 'CRM Enterprise', 'ThreatShield Guard', 'Integration Connect'];"
new_products_array = "const products = ['Apple iPhone 16', 'Samsung Galaxy S25', 'OnePlus 14', 'MacBook Air M4', 'Dell XPS 15', 'Lenovo ThinkBook 16', 'iPad Air', 'Samsung Galaxy Tab S10'];"

content = content.replace(old_products_array, new_products_array)

old_threatshield = "Maintain ThreatShield hardware token reserve counts above critical margins."
new_threatshield = "Maintain Apple iPhone 16 reserve counts above critical margins."

content = content.replace(old_threatshield, new_threatshield)

old_csv = 'const csvContent = "Customer Name,Product,Amount,Region,Status,Date\\nJohn Doe,Core Cloud Suite,150000.00,Maharashtra,Delivered,15/08/2026\\nJane Smith,CRM Enterprise,250000.00,Karnataka,Processing,16/08/2026";'
new_csv = 'const csvContent = "Customer Name,Product,Amount,Region,Status,Date\\nJohn Doe,Apple iPhone 16,150000.00,Maharashtra,Delivered,15/08/2026\\nJane Smith,MacBook Air M4,250000.00,Karnataka,Processing,16/08/2026";'

content = content.replace(old_csv, new_csv)

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("app.js updated")
