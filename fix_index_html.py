with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re

old_options = '''                        <option value="Core Cloud Suite">Core Cloud Suite</option>
                        <option value="CRM Enterprise">CRM Enterprise</option>
                        <option value="ThreatShield Guard">ThreatShield Guard</option>
                        <option value="Integration Connect">Integration Connect</option>'''

new_options = '''                        <option value="Apple iPhone 16">Apple iPhone 16</option>
                        <option value="Samsung Galaxy S25">Samsung Galaxy S25</option>
                        <option value="OnePlus 14">OnePlus 14</option>
                        <option value="MacBook Air M4">MacBook Air M4</option>
                        <option value="Dell XPS 15">Dell XPS 15</option>
                        <option value="Lenovo ThinkBook 16">Lenovo ThinkBook 16</option>
                        <option value="iPad Air">iPad Air</option>
                        <option value="Samsung Galaxy Tab S10">Samsung Galaxy Tab S10</option>'''

content = content.replace(old_options, new_options)

old_options_form = '''              <option value="Core Cloud Suite">Core Cloud Suite</option>
              <option value="CRM Enterprise">CRM Enterprise</option>
              <option value="ThreatShield Guard">ThreatShield Guard</option>
              <option value="Integration Connect">Integration Connect</option>'''

new_options_form = '''              <option value="Apple iPhone 16">Apple iPhone 16</option>
              <option value="Samsung Galaxy S25">Samsung Galaxy S25</option>
              <option value="OnePlus 14">OnePlus 14</option>
              <option value="MacBook Air M4">MacBook Air M4</option>
              <option value="Dell XPS 15">Dell XPS 15</option>
              <option value="Lenovo ThinkBook 16">Lenovo ThinkBook 16</option>
              <option value="iPad Air">iPad Air</option>
              <option value="Samsung Galaxy Tab S10">Samsung Galaxy Tab S10</option>'''

content = content.replace(old_options_form, new_options_form)

content = content.replace('>Core Cloud Suite<', '>Apple iPhone 16<')
content = content.replace('>CRM Enterprise<', '>MacBook Air M4<')
content = content.replace('>ThreatShield Guard<', '>Samsung Galaxy S25<')

content = content.replace('app.js?v=3.4.2', 'app.js?v=3.5.0')
content = content.replace('app.js?v=3.4.1', 'app.js?v=3.5.0')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("index.html updated")
