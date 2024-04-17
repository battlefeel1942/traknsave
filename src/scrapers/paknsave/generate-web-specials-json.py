import os
import json

def get_directory_structure(rootdir):
    """
    Creates a nested dictionary that represents the folder structure beneath rootdir,
    excluding the rootdir itself from the output and including only .json files.
    Directories are represented as arrays of .json files directly if they contain files.
    """
    dir_structure = {}
    rootdir = os.path.normpath(rootdir)  # Normalize the path to avoid issues with separators
    for path, dirs, files in os.walk(rootdir):
        # Normalize and strip the root directory, then split into components
        parts = os.path.normpath(path).replace(rootdir, '', 1).lstrip(os.sep).split(os.sep)
        current_level = dir_structure
        for part in parts:
            if part:  # Avoid creating an entry for empty string
                if part not in current_level:
                    current_level[part] = {}  # Initialize as dict initially
                current_level = current_level[part]
        # List only .json files in an array, not as dictionary keys
        json_files = [file for file in files if file.endswith('.json')]
        if json_files:  # Only set if there are .json files
            current_level.clear()  # Clear any existing directory keys if files are present
            current_level['files'] = json_files  # Use a 'files' key to store list of files directly

    return dir_structure

def save_structure_to_json(data, output_dir, filename):
    """
    Saves the dictionary data to a JSON file specified by output_dir and filename.
    Creates output_dir if it does not exist.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

# Set the directory to start the walk, excluding this root in the output
start_directory = "company"  # Adjust to your specific directory path

# Get the directory structure, focusing only on .json files
directory_structure = get_directory_structure(start_directory)

# Define the output directory and filename
output_directory = "web"  # Adjust to your specific output directory
output_filename = "specials.json"

# Save the directory structure to a JSON file
save_structure_to_json(directory_structure, output_directory, output_filename)

print(f"Directory structure has been saved to {os.path.join(output_directory, output_filename)}")
