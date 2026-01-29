import re


def clean_whitespace(text: str) -> str:
    # Normalize all whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def remove_headers_footers(text: str) -> str:
    patterns = [
        r'page\s*\d+\s*(of\s*\d+)?',          # Page 1, Page 1 of 10
        r'©\s?\d{4}.*',                       # Copyright
        r'all rights reserved.*',
        r'proceedings of.*?\d{4}',
        r'printed on.*',
        r'confidential.*',
    ]

    for p in patterns:
        text = re.sub(p, '', text, flags=re.IGNORECASE)

    return text


def remove_urls(text: str) -> str:
    # Replace URLs with token (better for embeddings than deleting)
    text = re.sub(r'http[s]?://[^\s]+', ' [URL] ', text, flags=re.I)
    text = re.sub(r'www\.[^\s]+', ' [URL] ', text, flags=re.I)
    return text


def remove_tables_figures(text: str) -> str:
    # Remove only Figure/Table labels, keep semantic description
    # Example: "Figure 2: Transformer architecture" -> "Transformer architecture"
    text = re.sub(r'\b(figure|fig\.?|table)\s+\d+[\s:\-]+', '', text, flags=re.I)
    return text


def remove_references_section(text: str) -> str:
    # Cut off everything after References / Bibliography
    parts = re.split(r'\b(references|bibliography)\b', text, flags=re.I)
    return parts[0]


def remove_garbage_lines(text: str) -> str:
    lines = text.splitlines()
    good_lines = []

    for line in lines:
        line_strip = line.strip()

        # Drop very short noisy lines
        if len(line_strip) < 3:
            continue

        # Drop lines that are only symbols (keep math + numbers)
        if re.fullmatch(r'[\W_]+', line_strip):
            continue

        # Drop pure page numbers
        if re.fullmatch(r'\d+', line_strip):
            continue

        good_lines.append(line_strip)

    return " ".join(good_lines)


def clean_text(text: str) -> str:
    if not text:
        return ""

    text = remove_references_section(text)
    text = remove_headers_footers(text)
    text = remove_urls(text)
    text = remove_tables_figures(text)
    text = remove_garbage_lines(text)
    text = clean_whitespace(text)

    return text









# import re

# def clean_whitespace(text):
#     text = re.sub(r'\s+', ' ', text)
#     return text.strip()


# def remove_common_headers(text):
#     patterns = [
#         r'Page \d+',
#         r'©\s?\d{4}.*',
#         r'Proceedings of.*?\d{4}'
#     ]
#     for p in patterns:
#         text = re.sub(p, '', text, flags=re.IGNORECASE)

#     re.sub(r'(table|figure)\s+\d+.*', '', text, flags=re.I)
#     return text

   
# def clean_text(text):
#     text = clean_whitespace(text)
#     text = remove_common_headers(text)
#     return text