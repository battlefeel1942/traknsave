import os

def format_filename(filename, lowercase_words):
    """Convert filename to readable format by removing extension, 
    replacing dashes with spaces, and capitalizing each word, 
    except for words in the lowercase_words set."""
    name_without_extension = os.path.splitext(filename)[0]
    formatted_name = ' '.join(word.capitalize() if word.lower() not in lowercase_words else word.lower() for word in name_without_extension.split('-'))
    return formatted_name

def generate_content(base_dir, url_prefix, lowercase_words):
    content = [
        "# PAK'nSave Deals Tracker\n\n",
        "This repository is updated daily with featured deals from Pak'nSave's [Deals Page](https://www.paknsave.co.nz/deals).\n",
        "These selected offers may include substantial discounts intended to attract customers.\n\n",
        "Additionally, Pak'nSave maintains a broader range of promotions on their [Shop Deals Page](https://www.paknsave.co.nz/shop/deals),\n",
        "which encompasses a variety of products available through their online shopping platform.\n\n"
    ]

    # Walk through the directory structure
    for root, dirs, files in os.walk(base_dir):
        # Calculate the indentation level based on directory depth
        indentation_level = root.count(os.sep) - base_dir.count(os.sep)

        # Write directory name
        dir_name = os.path.basename(root)
        if dir_name != os.path.basename(base_dir):  # Skip the base directory
            content.append("#" * (indentation_level + 1) + f" {format_filename(dir_name, lowercase_words)}\n")

        # Write file names with links, only for .md files
        for file in sorted(files):
            if file.endswith('.md'):  # Check if the file extension is .md
                relative_path = os.path.join(root, file).replace(base_dir, '').lstrip(os.sep)
                content.append(f"- [{format_filename(file, lowercase_words)}]({url_prefix}{relative_path})\n")

    return content

# Directory to start the walk
base_dir = "company/paknsave"
url_prefix = "https://github.com/battlefeel1942/traknsave/blob/main/company/paknsave/"
lowercase_words = {'and', 'or', 'the', 'a', 'an', 'to', 'of', 'in', 'for'}

# Generate content
content = generate_content(base_dir, url_prefix, lowercase_words)

# Write to the README.md file in /traknsave
with open("README.md", "w") as readme:
    readme.writelines(content)

print("README.md file generated successfully in /traknsave/!")
