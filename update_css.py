import re

def update_css():
    with open('style.css', 'r', encoding='utf-8') as f:
        content = f.read()

    css_addition = """
/* --- User Management Role Badges --- */
.role-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.role-ceo {
  background: rgba(139, 92, 246, 0.15);
  color: #8b5cf6;
}
[data-theme="dark"] .role-ceo {
  background: rgba(139, 92, 246, 0.2);
  color: #a78bfa;
}

.role-manager {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}
[data-theme="dark"] .role-manager {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
}

.role-analyst {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
}
[data-theme="dark"] .role-analyst {
  background: rgba(16, 185, 129, 0.2);
  color: #34d399;
}
"""
    if ".role-ceo {" not in content:
        with open('style.css', 'a', encoding='utf-8') as f:
            f.write(f"\n{css_addition}")

if __name__ == '__main__':
    update_css()
