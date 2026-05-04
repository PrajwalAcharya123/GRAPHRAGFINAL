import os
import re
from bs4 import BeautifulSoup


def get_sorted_html_files(folder):
    files = [f for f in os.listdir(folder) if f.endswith(".html")]

    def extract_number(filename):
        match = re.search(r'page_(\d+)', filename)
        return int(match.group(1)) if match else 0

    return sorted(files, key=extract_number)


def clean_html(soup):
    # Remove <style>
    for tag in soup.find_all("style"):
        tag.decompose()

    # Remove external CSS
    for tag in soup.find_all("link", rel="stylesheet"):
        tag.decompose()

    # Remove inline styles
    for tag in soup.find_all(True):
        if tag.has_attr("style"):
            del tag["style"]

    return soup


def merge_html_pages(input_folder, output_file):
    all_content = ""

    html_files = get_sorted_html_files(input_folder)

    if not html_files:
        print(" No HTML files found in:", input_folder)
        return

    for file in html_files:
        path = os.path.join(input_folder, file)
        print(f" Merging {file}...")

        with open(path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
            soup = clean_html(soup)

            if soup.body:
                all_content += f"<h2>{file}</h2>\n"
                all_content += str(soup.body) + "\n"
            else:
                all_content += str(soup) + "\n"

    final_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Combined HTML</title>
</head>
<body>
{all_content}
</body>
</html>
"""

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_html)

    print(f"\n Combined HTML saved at: {output_file}")