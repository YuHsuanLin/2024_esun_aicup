def read_markdown_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def clean_text(text):
    if not text: return ''
    pattern = re.compile(r'[\r\t\n\u3000\'" ]')
    # Use sub method to replace matched characters with an empty string
    cleaned_text = pattern.sub('', text)
    return cleaned_text


def read_md(main_folder, subfolder):
    image_pattern = r'!\[.*?\]\(.*?\)'
    markdown_file_path = f'{main_folder}/{subfolder}/{subfolder}.md'
    content = read_markdown_file(markdown_file_path)
    content = ''.join(
        re.split(image_pattern, content)
    ).strip()

    return content

