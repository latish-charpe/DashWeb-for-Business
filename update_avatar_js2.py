import re

def update_avatar_logic_2():
    with open('app.js', 'r', encoding='utf-8') as f:
        content = f.read()

    old_code = """      // Calculate dynamic initials
      let initials = '??';
      if (displayUser.length >= 2) {
          initials = displayUser.substring(0, 2).toUpperCase();
      } else if (displayUser.length === 1) {
          initials = displayUser.substring(0, 1).toUpperCase();
      }"""
      
    new_code = """      // Calculate dynamic initials based on username
      let initials = '??';
      const usrLower = displayUser.toLowerCase();
      if (usrLower === 'shrikant') {
          initials = 'SK';
      } else if (usrLower === 'manager') {
          initials = 'MG';
      } else if (usrLower === 'analyst') {
          initials = 'AN';
      } else {
          if (displayUser.length >= 2) {
              initials = displayUser.substring(0, 2).toUpperCase();
          } else if (displayUser.length === 1) {
              initials = displayUser.substring(0, 1).toUpperCase();
          }
      }"""

    if old_code in content:
        content = content.replace(old_code, new_code)
        with open('app.js', 'w', encoding='utf-8') as f:
            f.write(content)
    else:
        print("Could not find the target code block in app.js!")

if __name__ == '__main__':
    update_avatar_logic_2()
