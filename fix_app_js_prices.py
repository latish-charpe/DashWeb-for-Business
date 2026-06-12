with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

append_js = '''
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

  const productSelect = document.getElementById('product');
  const amountInput = document.getElementById('amount');

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
'''

if 'productPrices = {' not in content:
    content += append_js

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(content)
print('app.js updated with price autofill')
