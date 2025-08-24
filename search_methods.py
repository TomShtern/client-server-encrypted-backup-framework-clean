import ast
import sys

def find_methods_in_file(file_path, pattern):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        print(f"Syntax error in {file_path}: {e}")
        return []
    
    methods = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and pattern in node.name.lower():
            methods.append(node.name)
    
    return methods

if __name__ == "__main__":
    file_path = r"C:\Users\tom7s\Desktopp\Claude_Folder_2\Client_Server_Encrypted_Backup_Framework\flet_server_gui\utils\server_bridge.py"
    methods = find_methods_in_file(file_path, "mock")
    print("Methods containing 'mock':", methods)