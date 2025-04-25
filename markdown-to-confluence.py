import re
import os
import sys

# Maps common file extensions to Confluence code languages
LANGUAGE_MAP = {
    ".sh": "bash",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
    ".ini": "ini",
    ".conf": "ini",
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".go": "go",
    ".sql": "sql",
    ".html": "html",
    ".css": "css",
    ".md": "markdown",
}

def detect_language_from_filename(filename, fallback="bash"):
    _, ext = os.path.splitext(filename)
    return LANGUAGE_MAP.get(ext.lower(), fallback)

def convert_markdown_to_confluence(md_text):
    # Convert filename-prefixed code blocks like: /path/to/file.ext:\n```lang\ncode\n```
    def convert_code_with_filename(match):
        full_path = match.group("path")
        code = match.group("code").strip()
        filename = os.path.basename(full_path)
        lang = detect_language_from_filename(filename)
        return f"h3. {filename}\n" \
               f"{{code:title={filename}|language={lang}|linenumbers=true|collapse=false}}\n" \
               f"{code}\n" \
               f"{{code}}"

    md_text = re.sub(
        r"(?P<path>/[^\n]+):\n```[a-z]*\n(?P<code>.+?)```",
        convert_code_with_filename,
        md_text,
        flags=re.DOTALL
    )

    # Convert remaining code blocks: ```lang\ncode\n``` (not prefixed by filename)
    def convert_fenced_blocks(match):
        lang = match.group("lang") or "none"
        code = match.group("code").strip()
        return f"{{code:language={lang}}}\n{code}\n{{code}}"

    md_text = re.sub(
        r"```(?P<lang>[a-zA-Z0-9]*)\n(?P<code>.+?)```",
        convert_fenced_blocks,
        md_text,
        flags=re.DOTALL
    )

    # Headings
    md_text = re.sub(r'###### (.+)', r'h6. \1', md_text)
    md_text = re.sub(r'##### (.+)', r'h5. \1', md_text)
    md_text = re.sub(r'#### (.+)', r'h4. \1', md_text)
    md_text = re.sub(r'### (.+)', r'h3. \1', md_text)
    md_text = re.sub(r'## (.+)', r'h2. \1', md_text)
    md_text = re.sub(r'# (.+)', r'h1. \1', md_text)

    # Bold and Italic
    md_text = re.sub(r'\*\*\*(.+?)\*\*\*', r'_*\1*_', md_text)
    md_text = re.sub(r'\*\*(.+?)\*\*', r'*\1*', md_text)
    md_text = re.sub(r'\*(.+?)\*', r'_\1_', md_text)

    # Inline code
    md_text = re.sub(r'`([^`]+)`', r'{{\1}}', md_text)

    # Links
    md_text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'[\1|\2]', md_text)

    # Images
    md_text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'!\2!', md_text)

    # Blockquotes
    md_text = re.sub(r'^> (.+)', r'bq. \1', md_text, flags=re.MULTILINE)

    # Lists
    md_text = re.sub(r'^\s*[-*] ', r'* ', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^\s*\d+[.)] ', r'# ', md_text, flags=re.MULTILINE)

    return md_text

def main():
    if len(sys.argv) != 3:
        print("Usage: python markdown_to_confluence_full.py input.md output.txt")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, 'r', encoding='utf-8') as f:
        md_text = f.read()

    confluence_text = convert_markdown_to_confluence(md_text)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(confluence_text)

    print(f"[✓] Converted to Confluence format: {output_file}")

if __name__ == "__main__":
    main()

