import os
import re
import sys

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

def detect_language(filename, fallback="bash"):
    _, ext = os.path.splitext(filename)
    return LANGUAGE_MAP.get(ext.lower(), fallback)

def extract_code_blocks(text):
    # Find all code blocks and their position
    matches = list(re.finditer(r"(?P<filename>/[^\n]+):\n```(?P<lang>[a-zA-Z0-9]*)\n(?P<code>.+?)```", text, flags=re.DOTALL))
    code_segments = []
    last_end = 0
    for m in matches:
        code_segments.append({
            "type": "text",
            "content": text[last_end:m.start()]
        })
        filename = os.path.basename(m.group("filename"))
        lang = detect_language(filename, m.group("lang") or "bash")
        code = m.group("code").strip()
        confluence_block = f"h3. {filename}\n" \
               f"{{code:title={filename}|language={lang}|linenumbers=true|collapse=false}}\n" \
               f"{code}\n" \
               f"{{code}}"
        code_segments.append({
            "type": "code",
            "content": confluence_block
        })
        last_end = m.end()
    code_segments.append({
        "type": "text",
        "content": text[last_end:]
    })
    return code_segments

def convert_markdown_to_confluence(md_text):
    # Convert headings
    md_text = re.sub(r'###### (.+)', r'h6. \1', md_text)
    md_text = re.sub(r'##### (.+)', r'h5. \1', md_text)
    md_text = re.sub(r'#### (.+)', r'h4. \1', md_text)
    md_text = re.sub(r'### (.+)', r'h3. \1', md_text)
    md_text = re.sub(r'## (.+)', r'h2. \1', md_text)
    md_text = re.sub(r'# (.+)', r'h1. \1', md_text)

    # Convert emphasis (bold, italic)
    md_text = re.sub(r'\*\*\*(.+?)\*\*\*', r'_*\1*_', md_text)
    md_text = re.sub(r'\*\*(.+?)\*\*', r'*\1*', md_text)
    md_text = re.sub(r'\*(.+?)\*', r'_\1_', md_text)

    # Convert inline code
    md_text = re.sub(r'`([^`]+)`', r'{{\1}}', md_text)

    # Convert links
    md_text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'[\1|\2]', md_text)

    # Convert images
    md_text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'!\2!', md_text)

    # Convert blockquotes
    md_text = re.sub(r'^> (.+)', r'bq. \1', md_text, flags=re.MULTILINE)

    # Convert unordered/ordered lists
    md_text = re.sub(r'^\s*[-*] ', r'* ', md_text, flags=re.MULTILINE)
    md_text = re.sub(r'^\s*\d+[.)] ', r'# ', md_text, flags=re.MULTILINE)

    return md_text

def main():
    if len(sys.argv) != 3:
        print("Usage: python markdown_to_confluence_full_macro_v2.py input.md output.txt")
        sys.exit(1)

    input_file, output_file = sys.argv[1], sys.argv[2]

    with open(input_file, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    blocks = extract_code_blocks(raw_text)

    final_output = []
    for block in blocks:
        if block["type"] == "code":
            final_output.append(block["content"])
        else:
            converted = convert_markdown_to_confluence(block["content"])
            final_output.append(converted)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n\n".join(final_output))

    print(f"[✓] Converted to Confluence wiki format: {output_file}")

if __name__ == "__main__":
    main()
