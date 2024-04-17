import json
import os
import re
from collections import defaultdict
import sys

def slugify(value):
    """
    Convert spaces to hyphens. Remove characters that aren't alphanumerics,
    underscores, or hyphens.
    """
    value = str(value).lower()
    value = re.sub(r'(?u)[^-\w]', '', value)
    return re.sub(r'[-\s]+', '-', value)

def read_json(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
        return {(item["Product Name"], f"${item['Purchase Price']}", item["Expiry Date"]): filepath for item in data}

def hierarchy_format(files):
    hierarchy = {}
    for file in files:
        parts = file.split('/')
        d = hierarchy
        for part in parts[:-1]:
            if part not in d:
                d[part] = {}
            d = d[part]
        d[parts[-1].replace('.json', '')] = None  # Strip .json here

    return hierarchy

def custom_title(string):
    lowercase_words = {'and', 'or', 'the', 'a', 'an', 'to', 'of', 'in', 'for'}
    words = string.split()
    title_words = [word.title() if word.lower() not in lowercase_words else word.lower() for word in words]
    return ' '.join(title_words)

def write_hierarchy(f, hierarchy, indent=0):
    for key, value in hierarchy.items():
        formatted_key = custom_title(key.replace('-', ' '))
        f.write(f"{'  ' * indent}- {formatted_key}\n")
        if isinstance(value, dict):
            write_hierarchy(f, value, indent + 1)

def generate_title(base_header, condition):
    region = ""
    if sub_dir:
        region = custom_title(sub_dir.replace('-', ' '))
        region = f"{region} "

    condition_map = {
        "all": f"Items common to **all** {region}{base_header}",
        "some": f"Items common to **some** (but not all) {region}{base_header}",
        "unique": f"Items unique to **individual** {region}{base_header}"
    }

    return condition_map.get(condition)

def write_items_section(condition_name, condition):
    header = generate_title("PAK'nSAVE stores", condition_name)
    f.write(f"## {header}:\n")
    for files, expiry_groups in files_to_items.items():
        if condition(len(files)):

            for expiry_date, items in sorted(expiry_groups.items()):
                f.write(f"### Product(s) - {expiry_date} (deal ends) ###\n")
                for item in sorted(items, key=lambda x: x[0]):
                    f.write(f"- {item[0]} - **{item[1]}**\n")
                f.write("\n")

            # Indicate where these products are available
            f.write("#### Stores available: ####\n")

            # Location hierarchy listed after products
            stripped_files_list = [file.replace('company/paknsave/', '') for file in files]
            write_hierarchy(f, hierarchy_format(stripped_files_list))
            f.write("--- \n")

sub_dir = ""
if len(sys.argv) > 1:
    sub_dir = sys.argv[1]

start_dir = f"company/paknsave/{sub_dir}"
output_dir = "company/paknsave/deals/"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Determine output file name based on slugified version of sub_dir and place it inside /summary/
output_file_name = "product-locations.md" if not sub_dir else slugify(sub_dir) + ".md"
output_file_name = os.path.join(output_dir, output_file_name)

json_files = []
for root, dirs, files in os.walk(start_dir):
    for file in files:
        if file.endswith(".json"):
            json_files.append(os.path.join(root, file))

item_to_files = defaultdict(list)
for file in json_files:
    data = read_json(file)
    for item, filepath in data.items():
        item_to_files[item].append(filepath)

files_to_items = defaultdict(lambda: defaultdict(list))
for item, files in item_to_files.items():
    tuple_files = tuple(sorted(files))
    expiry_date = item[2]
    files_to_items[tuple_files][expiry_date].append(item)

with open(output_file_name, "w") as f:
    stripped_files = [file.replace('/company/paknsave/', '') for file in json_files]
    f.write("\n")

    write_items_section("all", lambda x: x == len(json_files))
    write_items_section("some", lambda x: 1 < x < len(json_files))
    write_items_section("unique", lambda x: x == 1)

print(f"Analysis complete. Check {output_file_name}.")
