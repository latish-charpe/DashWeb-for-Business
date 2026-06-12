import os

def search_files(directory, search_terms):
    for root, _, files in os.walk(directory):
        for file in files:
            if file in ['index.html', 'app.js', 'app.py', 'style.css']:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            for term in search_terms:
                                if term.lower() in line.lower():
                                    print(f"{file}:{i+1}: {line.strip()[:100]}")
                                    break # avoid duplicate prints for same line
                except Exception as e:
                    pass

search_files('C:\\dashweb', ['simulator', 'api-simulator', 'executive report'])
