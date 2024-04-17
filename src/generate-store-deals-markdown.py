import json
import os
import re
from collections import defaultdict

def slugify(value):
    """
    Convert spaces to hyphens. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Simplifies creating file names and URLs.
    """
    value = str(value).lower()
    value = re.sub(r'(?u)[^-\w]', '', value)
    return re.sub(r'[-\s]+', '-', value)

def read_json(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
        return [(item["Product Name"], item['Price'], item["Limit"], item["Multi"], item["Expiry Date"]) for item in data]

def custom_title(string):
    lowercase_words = {'and', 'or', 'the', 'a', 'an', 'to', 'of', 'in', 'for'}
    words = string.split()
    title_words = [word.title() if word.lower() not in lowercase_words else word.lower() for word in words]
    return ' '.join(title_words)

def write_items_to_md(f, grouped_items):
    for expiry_date, items in sorted(grouped_items.items()):
        f.write(f"## Product(s): {expiry_date} (deal ends)\n")
        for product_name, price, limit, multi in sorted(items):
            price_detail = f"{multi if multi else ''} ${price}{f' - {limit}' if limit else ''}".strip()
            f.write(f"- {product_name} - **{price_detail}**\n")
        f.write("\n")

start_dir = "company/paknsave/deals"
output_base_dir = "company/paknsave/deals"

json_files = [os.path.join(root, file) for root, dirs, files in os.walk(start_dir) for file in files if file.endswith(".json")]

for json_file in json_files:
    items = read_json(json_file)
    grouped_by_expiry = defaultdict(list)

    for product_name, price, limit, multi, expiry_date in items:
        grouped_by_expiry[expiry_date].append((product_name, price, limit, multi))

    relative_path = os.path.relpath(os.path.dirname(json_file), start_dir)
    store_output_dir = os.path.join(output_base_dir, relative_path)

    if not os.path.exists(store_output_dir):
        os.makedirs(store_output_dir)

    output_file_name = slugify(os.path.basename(json_file).replace(".json", "")) + ".md"
    output_file_path = os.path.join(store_output_dir, output_file_name)

    with open(output_file_path, "w") as f:
        f.write(f"# Products for {custom_title(os.path.basename(json_file).replace('.json', ''))} PAK'nSAVE\n\n")
        write_items_to_md(f, grouped_by_expiry)

print(f"Generated individual markdown files under {output_base_dir}.")
