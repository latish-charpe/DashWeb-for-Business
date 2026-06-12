with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1
for i, line in enumerate(lines):
    if 'id="view-api-simulator"' in line:
        start_idx = i
    if start_idx != -1 and '</section>' in line and i > start_idx + 10:
        end_idx = i + 1
        break

if start_idx != -1 and end_idx == -1:
    end_idx = len(lines)

print(f'Start: {start_idx}, End: {end_idx}')
if start_idx != -1:
    print('First lines:')
    print(''.join(lines[start_idx-2:start_idx+3]))
    print('Last lines:')
    print(''.join(lines[end_idx-3:end_idx+2]))
