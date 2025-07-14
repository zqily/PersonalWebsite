import os
import shutil
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# --- Configuration ---
# This script will ONLY convert files with extensions listed below.
# Add or remove extensions to control exactly what gets converted.
KNOWN_TEXT_EXTENSIONS = {
    # Common Code & Markup
    '.txt', '.md', '.rst', '.xml', '.html', '.htm', '.css', '.scss', '.less',
    '.js', 'json', '.ts', '.py', '.java', '.c', '.cpp', '.h', '.hpp', '.cs', '.rb', '.php',
    '.pl', '.sh', '.bat', '.ps1', '.go', '.swift', '.kt', '.kts', '.scala', '.lua',
    '.dart', '.vb', '.vbs', '.f', '.for', '.f90', '.pas', '.inc', '.asm', '.s',
    # Config & Data
    '.yml', '.yaml', '.csv', '.ini', '.cfg', '.conf', '.sql', '.properties',
    '.gradle', '.gitignore', '.dockerfile', '.tf', '.tfvars',
    # Other
    '.log', '.po', '.pot', '.srt', '.sub',
}

# Folders to completely ignore during the scan
# OPTIMIZATION: Using a set provides O(1) average time complexity for lookups.
FOLDERS_TO_IGNORE = {
    '.venv', 'venv', 'env', '.env',  # Virtual environments
    '__pycache__', '.pytest_cache', # Python cache
    '.git', '.svn', 'node_modules', # VCS and package managers
}

CONVERTED_FOLDER_NAME = "converted"
VERSION_PREFIX = "V"

# --- Core Logic Functions (Refactored for Clarity) ---

def setup_version_directory(script_dir):
    """
    Handles all versioning and directory setup logic.
    1. Ensures the base 'converted' directory exists.
    2. Scans for the highest existing version and any loose files.
    3. Moves loose files into a new version folder if they exist.
    4. Creates the target directory for this run's conversions.
    Returns the absolute path to the directory for new conversions.
    """
    converted_base_dir = os.path.join(script_dir, CONVERTED_FOLDER_NAME)
    os.makedirs(converted_base_dir, exist_ok=True)
    print(f"\nEnsured '{CONVERTED_FOLDER_NAME}' directory exists at: {converted_base_dir}")

    # Analyze the directory once to get version and loose files.
    version_pattern = re.compile(rf'^{VERSION_PREFIX}(\d+)')
    highest_num = 0
    loose_files = []

    if os.path.isdir(converted_base_dir):
        for entry in os.scandir(converted_base_dir):
            if entry.is_dir():
                match = version_pattern.match(entry.name)
                if match:
                    num = int(match.group(1))
                    if num > highest_num:
                        highest_num = num
            elif entry.is_file() and entry.name.lower().endswith('.txt'):
                loose_files.append(entry.path)

    next_version_num = highest_num + 1
    if loose_files:
        print(f"Found {len(loose_files)} loose file(s) in '{CONVERTED_FOLDER_NAME}'.")
        folder_for_loose_files = os.path.join(converted_base_dir, f"{VERSION_PREFIX}{next_version_num}")
        os.makedirs(folder_for_loose_files, exist_ok=True)
        print(f"Moving them to a new version folder: {folder_for_loose_files}")
        for f_path in loose_files:
            try:
                shutil.move(f_path, os.path.join(folder_for_loose_files, os.path.basename(f_path)))
            except Exception as e:
                print(f"  - Error moving '{os.path.basename(f_path)}': {e}")
        next_version_num += 1

    # Create the final directory for this run's conversions
    new_conversion_folder_name = f"{VERSION_PREFIX}{next_version_num}"
    new_conversion_path = os.path.join(converted_base_dir, new_conversion_folder_name)
    os.makedirs(new_conversion_path, exist_ok=True)
    print(f"New conversions will be placed in: {new_conversion_path}")
    return new_conversion_path


def scan_for_files(script_dir):
    """
    Scans the directory tree for files to be converted.
    It efficiently prunes ignored directories and the script itself.
    Returns a list of absolute file paths to convert.
    """
    files_to_convert = []
    script_path = os.path.abspath(__file__)
    # Convert to lowercase for case-insensitive comparison
    folders_to_ignore_lower = {f.lower() for f in FOLDERS_TO_IGNORE}

    for dirpath, dirnames, filenames in os.walk(script_dir, topdown=True):
        # Prune ignored directories to avoid scanning them at all.
        # This is a critical optimization.
        dirnames[:] = [d for d in dirnames if d != CONVERTED_FOLDER_NAME and d.lower() not in folders_to_ignore_lower]

        for filename in filenames:
            # OPTIMIZATION: Construct full path only once
            full_path = os.path.join(dirpath, filename)
            
            # Skip the script itself
            if full_path == script_path:
                continue

            # OPTIMIZATION: Check extension directly on the filename
            if os.path.splitext(filename)[1].lower() in KNOWN_TEXT_EXTENSIONS:
                files_to_convert.append(full_path)

    return files_to_convert

# --- Worker & Helper Functions ---

def read_file_content_with_fallbacks(filepath):
    """Tries to read file content using UTF-8, then latin-1 as a fallback."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(filepath, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception:
            return None # Failed to read with both
    except Exception:
        return None

def get_unique_filepath(directory, filename):
    """Ensures the target filepath is unique by appending a counter if needed."""
    output_filepath = os.path.join(directory, filename)
    if not os.path.exists(output_filepath):
        return output_filepath, filename

    base, ext = os.path.splitext(filename)
    counter = 1
    while True:
        new_filename = f"{base}_{counter}{ext}"
        new_filepath = os.path.join(directory, new_filename)
        if not os.path.exists(new_filepath):
            return new_filepath, new_filename
        counter += 1

def convert_single_file(original_filepath, output_dir, script_dir):
    """
    A self-contained worker function to process one file. Designed for concurrency.
    It now calculates the new filename itself, simplifying the main loop.
    Returns a status tuple: (status_code, original_path, message)
    """
    rel_path = os.path.relpath(original_filepath, script_dir)
    try:
        # --- REFACTOR: Filename logic is now encapsulated here ---
        original_filename = os.path.basename(original_filepath)
        base, ext = os.path.splitext(original_filename)
        ext_cleaned = ext.lstrip('.')
        new_filename_base = f"{base}.{ext_cleaned}.txt" if ext_cleaned else f"{base}.txt"
        
        output_filepath, final_new_filename = get_unique_filepath(output_dir, new_filename_base)

        content = read_file_content_with_fallbacks(original_filepath)
        if content is None:
            return (2, rel_path, f"Skipped: Read error (UTF-8/latin-1 failed).")

        with open(output_filepath, 'w', encoding='utf-8') as outfile:
            outfile.write(content)

        message = f"-> '{final_new_filename}'"
        if final_new_filename != new_filename_base:
            message += " (renamed)"
        return (1, rel_path, message)

    except Exception as e:
        return (3, rel_path, f"Failed: Unexpected error - {e}")

# --- Main Execution ---
def main():
    start_time = time.perf_counter()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Script running in: {script_dir}")
    print("Mode: Copy and Convert (Original files will not be modified)")
    print(f"INFO: Only files with extensions in KNOWN_TEXT_EXTENSIONS will be processed.")

    # 1. Setup versioning and get the target directory for this run's conversions
    new_version_path = setup_version_directory(script_dir)

    # 2. Scan for files to convert
    print("\nScanning for files with known text extensions...")
    files_to_convert = scan_for_files(script_dir)

    if not files_to_convert:
        print("\nNo new files with known text extensions were found to convert.")
        # Clean up the empty directory we created
        try:
            if not os.listdir(new_version_path):
                os.rmdir(new_version_path)
                print(f"Cleaned up empty version folder: {new_version_path}")
        except OSError as e:
            print(f"Could not remove empty version folder {new_version_path}: {e}")
        return

    # 3. Perform conversion using a ThreadPoolExecutor for I/O-bound tasks
    print(f"\nFound {len(files_to_convert)} files. Starting concurrent conversion...")
    
    converted_count = 0
    error_count = 0
    
    with ThreadPoolExecutor() as executor:
        # Submit all file conversion jobs to the pool
        future_to_path = {executor.submit(convert_single_file, filepath, new_version_path, script_dir): filepath for filepath in files_to_convert}

        # Process results as they are completed for responsive feedback
        for future in as_completed(future_to_path):
            status, rel_path, message = future.result()
            if status == 1: # Success
                print(f"  [OK]       '{rel_path}' {message}")
                converted_count += 1
            elif status == 2: # Read Error
                print(f"  [WARNING]  '{rel_path}' {message}")
            elif status == 3: # General Error
                print(f"  [ERROR]    '{rel_path}' {message}")
                error_count += 1
    
    end_time = time.perf_counter()
    duration = end_time - start_time

    print(f"\n--- Conversion Complete ---")
    print(f"Processed {len(files_to_convert)} files in {duration:.2f} seconds.")
    print(f"{converted_count} file(s) successfully converted into '{new_version_path}'.")
    if error_count > 0:
        print(f"{error_count} file(s) failed to convert due to errors.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n--- FATAL SCRIPT ERROR ---")
        print(f"An unexpected error stopped the script: {e}")
        import traceback
        traceback.print_exc()