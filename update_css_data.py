import re

def update_css():
    with open('style.css', 'r', encoding='utf-8') as f:
        content = f.read()

    css_addition = """
/* --- Data Management Module --- */
.csv-dropzone {
  border: 2px dashed var(--border-color);
  border-radius: 8px;
  padding: 40px 20px;
  text-align: center;
  background-color: var(--surface-color);
  transition: all 0.3s ease;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.csv-dropzone:hover {
  border-color: var(--primary);
  background-color: rgba(79, 70, 229, 0.05);
}

[data-theme="dark"] .csv-dropzone:hover {
  background-color: rgba(99, 102, 241, 0.1);
}

.table-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pagination {
  border-top: 1px solid var(--border-color);
  padding-top: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-info {
  font-size: 14px;
  color: var(--text-muted);
}
"""
    if ".csv-dropzone {" not in content:
        with open('style.css', 'a', encoding='utf-8') as f:
            f.write(f"\n{css_addition}")

if __name__ == '__main__':
    update_css()
