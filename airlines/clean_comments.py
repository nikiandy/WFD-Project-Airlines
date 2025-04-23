import os
import re
import sys

def clean_comments_py(content, file_path):

    content = re.sub(r'', '', content, flags=re.DOTALL)
    content = re.sub(r"", '', content, flags=re.DOTALL)

    content = re.sub(r'

    content = re.sub(r'\n\s*\n+', '\n\n', content)

    if 'views.py' in file_path:

        content = add_view_comments(content, file_path)
    elif 'models.py' in file_path:

        content = add_model_comments(content)
    elif 'forms.py' in file_path:

        content = add_form_comments(content)
    elif 'urls.py' in file_path:

        content = add_url_comments(content)
    elif 'admin.py' in file_path:

        content = add_admin_comments(content)
    elif 'tests.py' in file_path:

        content = add_test_comments(content)

    return content

def clean_comments_js(content):

    content = re.sub(r'/\*[\s\S]*?\*/', '', content)

    content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)

    content = re.sub(r'\n\s*\n+', '\n\n', content)

    content = add_js_comments(content)

    return content

def clean_comments_css(content):

    content = re.sub(r'/\*[\s\S]*?\*/', '', content)

    content = re.sub(r'\n\s*\n+', '\n\n', content)

    content = add_css_comments(content)

    return content

def add_view_comments(content, file_path):

    use_case_map = {

        'flights/views.py': {
            'flight_search': '
            'flight_detail': '
            'flight_status': '
            'flight_management': '
        },

        'bookings/views.py': {
            'booking_create': '
            'booking_detail': '
            'booking_payment': '
            'booking_cancel': '
        },

        'accounts/views.py': {
            'profile': '
            'login': '
            'register': '
            'password_reset': '
        },

        'passengers/views.py': {
            'passenger_profile': '
            'update_preferences': '
        },
    }

    app_use_cases = {}
    for app_path, cases in use_case_map.items():
        if app_path in file_path:
            app_use_cases = cases
            break

    for func_name, use_case in app_use_cases.items():
        pattern = f'def\\s+{func_name}\\s*\\('
        if re.search(pattern, content):
            content = re.sub(pattern, f'{use_case}\ndef {func_name}(', content)

    content = re.sub(r'def\s+(\w+)\s*\([^)]*\):', 
                     lambda m: f"
                     if not re.search(f"
                     content)

    content = re.sub(r'class\s+(\w+)View\s*\(', 
                     lambda m: f"
                     content)

    crud_patterns = {
        r'def\s+create_': '
        r'def\s+get_': '
        r'def\s+update_': '
        r'def\s+delete_': '
        r'def\s+list_': '
    }

    for pattern, comment in crud_patterns.items():
        content = re.sub(pattern, comment + pattern.replace(r'def\s+', 'def '), content)

    return content

def add_model_comments(content):

    content = re.sub(r'class\s+(\w+)\s*\(models\.Model\):', 
                    lambda m: f"
                    content)

    content = re.sub(r'class\s+(\w+)Manager\s*\(models\.Manager\):', 
                    lambda m: f"
                    content)

    method_patterns = {
        r'def\s+save': '
        r'def\s+__str__': '
        r'def\s+get_absolute_url': '
        r'def\s+clean': '
    }

    for pattern, comment in method_patterns.items():
        content = re.sub(f'({pattern}\\s*\\([^)]*\\):)', f'{comment}\n    \\1', content)

    return content

def add_form_comments(content):

    content = re.sub(r'class\s+(\w+)Form\s*\(', 
                    lambda m: f"
                    content)

    content = re.sub(r'def\s+clean_(\w+)', 
                    lambda m: f"
                    content)

    return content

def add_url_comments(content):

    content = re.sub(r'path\(\s*[\'"]([^\'"]+)[\'"]',
                    lambda m: f"
                    content)

    content = re.sub(r'(urlpatterns\s*=\s*\[)',
                    '
                    content)

    return content

def add_admin_comments(content):

    content = re.sub(r'class\s+(\w+)Admin\s*\(admin\.ModelAdmin\):',
                    lambda m: f"
                    content)

    content = re.sub(r'admin\.site\.register\s*\(\s*(\w+)\s*,\s*(\w+)Admin\s*\)',
                    lambda m: f"
                    content)

    return content

def add_test_comments(content):

    content = re.sub(r'class\s+(\w+)Test\s*\(TestCase\):',
                    lambda m: f"
                    content)

    content = re.sub(r'def\s+test_(\w+)',
                    lambda m: f"
                    content)

    return content

def add_js_comments(content):

    sections = {
        "document.addEventListener\\('DOMContentLoaded'": "// Initialize page when DOM is loaded",
        "function\\s+\\w+\\s*\\(": "// Function definition",
        "\\$\\(document\\).ready": "// jQuery document ready handler",
        "fetch\\(": "// API request to server",
        "\\$\\.ajax\\(": "// AJAX request to server",
        "const\\s+\\w+\\s*=\\s*document\\.querySelector": "// DOM element selection",
        "if\\s*\\(": "// Conditional logic",
        "for\\s*\\(": "// Loop through items",
        "async\\s+function": "// Asynchronous function",
        "\\.addEventListener\\(": "// Event handler attachment",
    }

    for pattern, comment in sections.items():

        lines = content.split('\n')
        new_lines = []
        for line in lines:
            match = re.search(f'^\\s*({pattern})', line)
            if match and not line.strip().startswith('//'):
                new_lines.append(f"{comment}")
                new_lines.append(line)
            else:
                new_lines.append(line)
        content = '\n'.join(new_lines)

    return content

def add_css_comments(content):

    sections = {
        "body\\s*{": "/* Base body styles */",
        "\\.container": "/* Container layout */",
        "\\.header": "/* Header section */",
        "\\.footer": "/* Footer section */",
        "\\.nav": "/* Navigation elements */",
        "@media": "/* Responsive design rules */",
        "\\.btn": "/* Button styling */",
        "\\.form": "/* Form elements */",
        "\\.card": "/* Card components */",
        "\\.modal": "/* Modal dialogs */",
        "\\.table": "/* Table styling */",
        "\\.alert": "/* Alert messages */",
        "
    }

    for pattern, comment in sections.items():

        lines = content.split('\n')
        new_lines = []
        for line in lines:
            match = re.search(f'^\\s*({pattern})', line)
            if match and not (line.strip().startswith('/*') or line.strip().startswith('*/')):
                new_lines.append(f"{comment}")
                new_lines.append(line)
            else:
                new_lines.append(line)
        content = '\n'.join(new_lines)

    return content

def process_file(file_path):
    print(f"Processing {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        if any(skip in file_path for skip in ['.git', '.venv', 'venv', 'migrations']):
            print(f"Skipping {file_path} (excluded directory)")
            return

        if file_path.endswith('.py'):
            modified_content = clean_comments_py(content, file_path)
        elif file_path.endswith('.js'):
            modified_content = clean_comments_js(content)
        elif file_path.endswith('.css'):
            modified_content = clean_comments_css(content)
        elif file_path.endswith('.html'):

            modified_content = content

            script_tags = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
            for script in script_tags:
                if script.strip():  
                    cleaned_script = clean_comments_js(script)
                    if script != cleaned_script:
                        modified_content = modified_content.replace(script, cleaned_script)

            style_tags = re.findall(r'<style[^>]*>(.*?)</style>', content, re.DOTALL)
            for style in style_tags:
                if style.strip():  
                    cleaned_style = clean_comments_css(style)
                    if style != cleaned_style:
                        modified_content = modified_content.replace(style, cleaned_style)
        else:
            print(f"Skipping unsupported file type: {file_path}")
            return

        if modified_content != content:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(modified_content)
            print(f"Cleaned comments in {file_path}")
        else:
            print(f"No changes made to {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")

def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.py', '.js', '.css', '.html')):
                file_path = os.path.join(root, file)
                process_file(file_path)

def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if os.path.isfile(path) and path.endswith(('.py', '.js', '.css', '.html')):
            process_file(path)
        elif os.path.isdir(path):
            process_directory(path)
        else:
            print(f"Invalid path: {path}")
    else:

        process_directory('.')

if __name__ == '__main__':
    main() 