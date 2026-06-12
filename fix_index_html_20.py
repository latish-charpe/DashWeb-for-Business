with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_options = '''                        <option value="Apple iPhone 16">Apple iPhone 16</option>
                        <option value="Samsung Galaxy S25">Samsung Galaxy S25</option>
                        <option value="OnePlus 14">OnePlus 14</option>
                        <option value="MacBook Air M4">MacBook Air M4</option>
                        <option value="Dell XPS 15">Dell XPS 15</option>
                        <option value="Lenovo ThinkBook 16">Lenovo ThinkBook 16</option>
                        <option value="iPad Air">iPad Air</option>
                        <option value="Samsung Galaxy Tab S10">Samsung Galaxy Tab S10</option>'''

new_options = '''                        <option value="Apple iPhone 16">Apple iPhone 16</option>
                        <option value="Apple iPhone 16 Pro">Apple iPhone 16 Pro</option>
                        <option value="Samsung Galaxy S25">Samsung Galaxy S25</option>
                        <option value="Samsung Galaxy S25 Ultra">Samsung Galaxy S25 Ultra</option>
                        <option value="OnePlus 14">OnePlus 14</option>
                        <option value="Google Pixel 10">Google Pixel 10</option>
                        <option value="MacBook Air M4">MacBook Air M4</option>
                        <option value="MacBook Pro M4">MacBook Pro M4</option>
                        <option value="Dell XPS 15">Dell XPS 15</option>
                        <option value="HP Pavilion 15">HP Pavilion 15</option>
                        <option value="Lenovo ThinkBook 16">Lenovo ThinkBook 16</option>
                        <option value="ASUS ROG Strix G16">ASUS ROG Strix G16</option>
                        <option value="iPad Air">iPad Air</option>
                        <option value="Samsung Galaxy Tab S10">Samsung Galaxy Tab S10</option>
                        <option value="Apple Watch Series 11">Apple Watch Series 11</option>
                        <option value="Samsung Galaxy Watch 8">Samsung Galaxy Watch 8</option>
                        <option value="AirPods Pro 3">AirPods Pro 3</option>
                        <option value="Sony WH-1000XM6">Sony WH-1000XM6</option>
                        <option value="JBL Flip 7">JBL Flip 7</option>
                        <option value="Logitech MX Master 4">Logitech MX Master 4</option>'''

content = content.replace(old_options, new_options)

old_options_form = '''              <option value="Apple iPhone 16">Apple iPhone 16</option>
              <option value="Samsung Galaxy S25">Samsung Galaxy S25</option>
              <option value="OnePlus 14">OnePlus 14</option>
              <option value="MacBook Air M4">MacBook Air M4</option>
              <option value="Dell XPS 15">Dell XPS 15</option>
              <option value="Lenovo ThinkBook 16">Lenovo ThinkBook 16</option>
              <option value="iPad Air">iPad Air</option>
              <option value="Samsung Galaxy Tab S10">Samsung Galaxy Tab S10</option>'''

new_options_form = '''              <option value="Apple iPhone 16">Apple iPhone 16</option>
              <option value="Apple iPhone 16 Pro">Apple iPhone 16 Pro</option>
              <option value="Samsung Galaxy S25">Samsung Galaxy S25</option>
              <option value="Samsung Galaxy S25 Ultra">Samsung Galaxy S25 Ultra</option>
              <option value="OnePlus 14">OnePlus 14</option>
              <option value="Google Pixel 10">Google Pixel 10</option>
              <option value="MacBook Air M4">MacBook Air M4</option>
              <option value="MacBook Pro M4">MacBook Pro M4</option>
              <option value="Dell XPS 15">Dell XPS 15</option>
              <option value="HP Pavilion 15">HP Pavilion 15</option>
              <option value="Lenovo ThinkBook 16">Lenovo ThinkBook 16</option>
              <option value="ASUS ROG Strix G16">ASUS ROG Strix G16</option>
              <option value="iPad Air">iPad Air</option>
              <option value="Samsung Galaxy Tab S10">Samsung Galaxy Tab S10</option>
              <option value="Apple Watch Series 11">Apple Watch Series 11</option>
              <option value="Samsung Galaxy Watch 8">Samsung Galaxy Watch 8</option>
              <option value="AirPods Pro 3">AirPods Pro 3</option>
              <option value="Sony WH-1000XM6">Sony WH-1000XM6</option>
              <option value="JBL Flip 7">JBL Flip 7</option>
              <option value="Logitech MX Master 4">Logitech MX Master 4</option>'''

content = content.replace(old_options_form, new_options_form)

content = content.replace('app.js?v=3.5.0', 'app.js?v=3.6.0')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("index.html updated")
