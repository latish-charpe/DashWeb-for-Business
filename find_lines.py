with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'data-view="api-simulator"' in line:
        start_nav = i
    if '<!-- VIEW 9: API SIMULATOR -->' in line:
        start_view = i
    if '<!-- VIEW 8: SETTINGS -->' in line:
        end_settings = i

print(f'Nav start: {start_nav}')
print('Nav block:')
print(''.join(lines[start_nav:start_nav+10]))
print(f'View start: {start_view}')
