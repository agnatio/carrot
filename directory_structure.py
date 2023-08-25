import os

def list_files(startpath):
    # Initial display for the root directory
    print("/")
    
    for root, dirs, files in os.walk(startpath):
        # Skip the 'venv' folder and its subdirectories
        if "venv" in dirs:
            dirs.remove("venv")
        if ".git" in dirs:
            dirs.remove(".git")
        
        if "__pycache__" in dirs:
            dirs.remove("__pycache__")

        level = root.replace(startpath, '').count(os.sep)
        
        # Adjust the indentations using the new characters
        indent = ' ' * 4 * (level - 1) + '├── ' if level > 0 else ''
        subindent = ' ' * 4 * level + '│   ├── '
        
        # Skip printing the root directory again
        if root != startpath:
            print('{}{}/'.format(indent, os.path.basename(root)))
        
        for f in files:
            print('{}{}'.format(subindent, f))

# List the structure of the current directory, skipping the venv and __pycache__ folders
list_files(os.path.dirname(os.path.abspath(__file__)))
