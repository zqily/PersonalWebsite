# ########################################################################## #
# #                                                                        # #
# #   !!!   D A N G E R   -   D E S T R U C T I V E   S C R I P T   !!!    # #
# #                                                                        # #
# #   This script will DELETE the original source files and their          # #
# #   containing folders after they are successfully converted.            # #
# #                                                                        # #
# #   USE WITH EXTREME CAUTION. THERE IS NO UNDO.                          # #
# #   ALWAYS HAVE A BACKUP OR USE THIS ON COPIES OF YOUR DATA.             # #
# #                                                                        # #
# ########################################################################## #

import os
import shutil
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# --- Configuration ---
# This script will ONLY convert files with extensions listed below.
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
FOLDERS_TO_IGNORE = {
    '.venv', 'venv', 'env', '.env',  # Virtual environments
    '__pycache__', '.pytest_cache', # Python cache
    '.git', '.svn', 'node_modules', # VCS and package managers
}

CONVERTED_FOLDER_NAME = "converted"
VERSION_PREFIX = "V"

# --- Core Logic Functions (Refactored for Clarity) ---

def setup_version_directory(script_dir):
    """Identical to the previous version. Handles all versioning and directory setup."""
    # (This function is unchanged from the non-destructive version)
    converted_base_dir = os.path.join(script_dir, CONVERTED_FOLDER_NAME)
    os.makedirs(converted_base_dir, exist_ok=True)
    print(f"\nEnsured '{CONVERTED_FOLDER_NAME}' directory exists at: {converted_base_dir}")

    version_pattern = re.compile(rf'^{VERSION_PREFIX}(\d+)')
    highest_num, loose_files = 0, []
    if os.path.isdir(converted_base_dir):
        for entry in os.scandir(converted_base_dir):
            if entry.is_dir():
                match = version_pattern.match(entry.name)
                if match:
                    num = int(match.group(1))
                    if num > highest_num: highest_num = num
            elif entry.is_file() and entry.name.lower().endswith('.txt'):
                loose_files.append(entry.path)

    next_version_num = highest_num + 1
    if loose_files:
        print(f"Found {len(loose_files)} loose file(s) in '{CONVERTED_FOLDER_NAME}'.")
        folder_for_loose_files = os.path.join(converted_base_dir, f"{VERSION_PREFIX}{next_version_num}")
        os.makedirs(folder_for_loose_files, exist_ok=True)
        print(f"Moving them to a new version folder: {folder_for_loose_files}")
        for f_path in loose_files:
            try: shutil.move(f_path, os.path.join(folder_for_loose_files, os.path.basename(f_path)))
            except Exception as e: print(f"  - Error moving '{os.path.basename(f_path)}': {e}")
        next_version_num += 1

    new_conversion_folder_name = f"{VERSION_PREFIX}{next_version_num}"
    new_conversion_path = os.path.join(converted_base_dir, new_conversion_folder_name)
    os.makedirs(new_conversion_path, exist_ok=True)
    print(f"New conversions will be moved to: {new_conversion_path}")
    return new_conversion_path

def scan_for_files(script_dir):
    """
    Scans for convertible files and ALSO collects the parent directories.
    Returns a tuple: (list_of_files_to_convert, set_of_directories_scanned)
    """
    files_to_convert = []
    # Using a set automatically handles duplicate directory paths
    directories_scanned = set()
    script_path = os.path.abspath(__file__)
    folders_to_ignore_lower = {f.lower() for f in FOLDERS_TO_IGNORE}

    for dirpath, dirnames, filenames in os.walk(script_dir, topdown=True):
        dirnames[:] = [d for d in dirnames if d != CONVERTED_FOLDER_NAME and d.lower() not in folders_to_ignore_lower]

        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            if full_path == script_path:
                continue

            if os.path.splitext(filename)[1].lower() in KNOWN_TEXT_EXTENSIONS:
                files_to_convert.append(full_path)
                # MODIFICATION: Track the parent directory for future cleanup
                directories_scanned.add(dirpath)

    return files_to_convert, directories_scanned

def cleanup_empty_directories(dir_set):
    """
    Attempts to remove directories that are now empty after files were moved.
    It sorts paths by length (depth) to remove children before parents.
    """
    if not dir_set:
        return
    
    print("\nAttempting to clean up empty source directories...")
    cleaned_count = 0
    # Sort by path length, descending. This ensures we process e.g., 'a/b/c' before 'a/b'.
    for path in sorted(list(dir_set), key=len, reverse=True):
        try:
            # os.rmdir will only succeed if the directory is empty.
            os.rmdir(path)
            print(f"  - Removed empty directory: '{os.path.relpath(path)}'")
            cleaned_count += 1
        except OSError:
            # This is expected if the directory contains non-converted files or subdirectories.
            pass
    if cleaned_count > 0:
        print(f"Cleanup complete. Removed {cleaned_count} empty directories.")
    else:
        print("No empty source directories to remove.")


# --- Worker & Helper Functions ---

def read_file_content_with_fallbacks(filepath):
    """Tries to read file content using UTF-8, then latin-1 as a fallback."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f: return f.read()
    except UnicodeDecodeError:
        try:
            with open(filepath, 'r', encoding='latin-1') as f: return f.read()
        except Exception: return None
    except Exception: return None

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
        if not os.path.exists(new_filepath): return new_filepath, new_filename
        counter += 1

def convert_and_move_single_file(original_filepath, output_dir, script_dir):
    """
    Worker function: Converts a single file, writes it to the destination,
    and then DELETES the original file upon success.
    """
    rel_path = os.path.relpath(original_filepath, script_dir)
    try:
        original_filename = os.path.basename(original_filepath)
        base, ext = os.path.splitext(original_filename)
        ext_cleaned = ext.lstrip('.')
        new_filename_base = f"{base}.{ext_cleaned}.txt" if ext_cleaned else f"{base}.txt"
        
        output_filepath, final_new_filename = get_unique_filepath(output_dir, new_filename_base)

        content = read_file_content_with_fallbacks(original_filepath)
        if content is None:
            return (2, rel_path, "Skipped: Read error. ORIGINAL FILE NOT DELETED.")

        # Write the new file first. If this fails, we won't delete the original.
        with open(output_filepath, 'w', encoding='utf-8') as outfile:
            outfile.write(content)

        # DESTRUCTIVE ACTION: Delete the original file ONLY after successful write.
        try:
            os.remove(original_filepath)
            message = f"-> '{final_new_filename}' (Original DELETED)"
            if final_new_filename != new_filename_base:
                message += " (renamed)"
            return (1, rel_path, message)
        except OSError as e:
            return (3, rel_path, f"Converted, but FAILED TO DELETE ORIGINAL: {e}")

    except Exception as e:
        return (3, rel_path, f"Failed: Unexpected error - {e}. ORIGINAL FILE NOT DELETED.")

# --- Main Execution ---
def main():
    start_time = time.perf_counter()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # CRITICAL WARNING
    print("="*60)
    print("!!! DANGER: DESTRUCTIVE MODE ENABLED !!!")
    print("This script will DELETE original files after conversion.")
    print("Press CTRL+C now to abort if this is not what you want.")
    print("="*60)
    time.sleep(3) # Give user a moment to read and react

    print(f"Script running in: {script_dir}")
    print("Mode: Move and Convert (Original files WILL BE DELETED)")

    # 1. Setup versioning and get the target directory
    new_version_path = setup_version_directory(script_dir)

    # 2. Scan for files and the directories they are in
    print("\nScanning for files to move and convert...")
    files_to_convert, source_dirs = scan_for_files(script_dir)

    if not files_to_convert:
        print("\nNo files with known text extensions were found to convert.")
        try:
            if not os.listdir(new_version_path):
                os.rmdir(new_version_path)
                print(f"Cleaned up empty version folder: {new_version_path}")
        except OSError as e:
            print(f"Could not remove empty version folder {new_version_path}: {e}")
        return

    # 3. Perform conversion and deletion concurrently
    print(f"\nFound {len(files_to_convert)} files. Starting concurrent move & convert...")
    converted_count, error_count = 0, 0
    
    with ThreadPoolExecutor() as executor:
        future_to_path = {executor.submit(convert_and_move_single_file, fp, new_version_path, script_dir): fp for fp in files_to_convert}
        for future in as_completed(future_to_path):
            status, rel_path, message = future.result()
            if status == 1: # Success
                print(f"  [MOVED]    '{rel_path}' {message}")
                converted_count += 1
            elif status == 2: # Read Error (Warning)
                print(f"  [WARNING]  '{rel_path}' {message}")
            elif status == 3: # Write/Delete Error
                print(f"  [ERROR]    '{rel_path}' {message}")
                error_count += 1
    
    # 4. Clean up the empty source directories
    cleanup_empty_directories(source_dirs)
    
    end_time = time.perf_counter()
    duration = end_time - start_time

    print(f"\n--- Conversion Complete ---")
    print(f"Processed {len(files_to_convert)} files in {duration:.2f} seconds.")
    print(f"{converted_count} file(s) successfully moved and converted to '{new_version_path}'.")
    if error_count > 0:
        print(f"{error_count} file(s) encountered errors. Some originals may not have been deleted.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation aborted by user. No more files will be processed.")
    except Exception as e:
        print(f"\n--- FATAL SCRIPT ERROR ---")
        print(f"An unexpected error stopped the script: {e}")
        import traceback
        traceback.print_exc()