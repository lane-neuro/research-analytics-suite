import os
import sys


def list_directory_contents(dir_path, depth=3, level=0):
    if level > depth:
        return
    try:
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            print('    ' * level + '|-- ' + item)
            if os.path.isdir(item_path):
                list_directory_contents(item_path, depth, level + 1)
    except UnicodeEncodeError as e:
        print(f"Skipping {dir_path} due to encoding error: {e}")

# Set the path to your project root and desired depth
project_root = '.'  # '.' represents the current directory
depth = 3

if __name__ == "__main__":
    # Redirect stdout to handle UTF-8 encoding
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
    print(project_root)
    list_directory_contents(project_root, depth)
