import os
import re
import sys

def remove_comments(content):

    content = re.sub(r'', '', content, flags=re.DOTALL)
    content = re.sub(r"", '', content, flags=re.DOTALL)

    content = re.sub(r'

    content = re.sub(r'\n\s*\n+', '\n\n', content)

    return content

def process_file(file_path):
    print(f"Processing {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        if '"""' not in content and "'''" not in content and '
            print(f"No comments found in {file_path}, skipping")
            return

        modified_content = remove_comments(content)

        if modified_content != content:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(modified_content)
            print(f"Removed comments from {file_path}")
        else:
            print(f"No changes made to {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")

def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                process_file(file_path)

def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if os.path.isfile(path) and path.endswith('.py'):
            process_file(path)
        elif os.path.isdir(path):
            process_directory(path)
        else:
            print(f"Invalid path: {path}")
    else:

        process_directory('.')

if __name__ == '__main__':
    main() 