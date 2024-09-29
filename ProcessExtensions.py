import os
import sys
import shutil
import hashlib
from datetime import datetime

# Global flags
preview = False
debug = False

def read_extensions_from_file(input_file):
    print(f"Reading extensions from: {input_file}")
    with open(input_file, 'r') as f:
        raw_content = f.read().strip()
        extensions = [ext.strip() for ext in raw_content.replace('\n', ',').split(',')]
        extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]
        print(f"Extensions read: {extensions}")
        return extensions

def create_target_directory(target_base, creation_time):
    date_path = datetime.fromtimestamp(creation_time).strftime('%Y/%m/%d')
    target_dir = os.path.join(target_base, date_path)
    
    if not os.path.exists(target_dir):
        print(f"Creating directory: {target_dir}")
        if not preview:
            os.makedirs(target_dir)
    
    return target_dir

def calculate_file_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def generate_incremental_filename(base_filename, extension, target_dir):
    counter = 1
    new_filename = f"{base_filename}_{counter:03d}{extension}"
    while os.path.exists(os.path.join(target_dir, new_filename)):
        counter += 1
        new_filename = f"{base_filename}_{counter:03d}{extension}"
    return new_filename

def log_index(file_path, action, index_file):
    with open(index_file, 'a') as log_file:
        if action == 'moved':
            log_file.write(f"{file_path} -> Moved\n")
        elif action == 'deleted':
            log_file.write(f"{file_path} -> Deleted (Duplicate Found)\n")

def log_verify(target_file_path, verify_script):
    with open(verify_script, 'a') as verify_file:
        # Write an ls -l command for the moved file path
        verify_file.write(f"ls -l '{target_file_path}'\n")

def log_failure(source_file, target_file, error_message, failure_file):
    with open(failure_file, 'a') as fail_file:
        if target_file:
            fail_file.write(f"Failure: {error_message} -> Source: {source_file}, Target: {target_file}\n")
        else:
            fail_file.write(f"Failure: {error_message} -> Source: {source_file}\n")

def move_files_by_extension(source_dir, target_dir, extensions, index_file, verify_script, failure_file, preview, debug):
    print(f"Scanning source directory: {source_dir}")
    
    for root, dirs, files in os.walk(source_dir):
        if debug:
            print(f"Checking directory: {root}")
        
        for file in files:
            _, ext = os.path.splitext(file)
            
            if ext in extensions:
                file_path = os.path.join(root, file)
                print(f"Found matching file: {file_path} with extension {ext}")
                
                try:
                    try:
                        creation_time = os.stat(file_path).st_ctime
                    except AttributeError:
                        creation_time = os.path.getmtime(file_path)

                    target_subdir = create_target_directory(target_dir, creation_time)
                    target_file_path = os.path.join(target_subdir, file)

                    if os.path.exists(target_file_path):
                        print(f"File already exists: {target_file_path}")

                        source_hash = calculate_file_hash(file_path)
                        target_hash = calculate_file_hash(target_file_path)

                        if source_hash == target_hash:
                            print(f"Files are identical. Deleting source file: {file_path}")
                            if not preview:
                                try:
                                    os.remove(file_path)
                                    log_index(file_path, 'deleted', index_file)
                                except Exception as e:
                                    log_failure(file_path, None, f"Failed to delete file: {e}", failure_file)
                            else:
                                print(f"Preview: Would delete file: {file_path}")
                        else:
                            print(f"Files are different. Generating new filename for: {file_path}")
                            base_filename, extension = os.path.splitext(file)
                            new_filename = generate_incremental_filename(base_filename, extension, target_subdir)
                            new_target_file_path = os.path.join(target_subdir, new_filename)
                            print(f"Preview: Would move: {file_path} -> {new_target_file_path}")
                            if not preview:
                                try:
                                    shutil.move(file_path, new_target_file_path)
                                    log_index(file_path, 'moved', index_file)
                                    log_verify(new_target_file_path, verify_script)
                                except Exception as e:
                                    log_failure(file_path, new_target_file_path, f"Failed to move file: {e}", failure_file)
                    else:
                        print(f"Preview: Would move: {file_path} -> {target_file_path}")
                        if not preview:
                            try:
                                shutil.move(file_path, target_file_path)
                                log_index(file_path, 'moved', index_file)
                                log_verify(target_file_path, verify_script)
                            except Exception as e:
                                log_failure(file_path, target_file_path, f"Failed to move file: {e}", failure_file)

                except FileNotFoundError:
                    print(f"File not found: {file_path}")
                    log_failure(file_path, None, "File not found", failure_file)
                except PermissionError:
                    print(f"Permission denied while accessing file: {file_path}")
                    log_failure(file_path, None, "Permission denied", failure_file)
                except Exception as e:
                    print(f"An unexpected error occurred with file {file_path}: {e}")
                    log_failure(file_path, None, f"Unexpected error: {e}", failure_file)

            elif debug:
                print(f"Skipping file: {file} (extension {ext} not in list)")

def main():
    global preview, debug

    if len(sys.argv) < 4 or len(sys.argv) > 6:
        print("Usage: python script.py <inputListFile> <SourceDirectory> <TargetDirectory> [--preview] [--debug]")
        sys.exit(1)

    input_list_file = sys.argv[1]
    source_directory = sys.argv[2]
    target_directory = sys.argv[3]

    # Process optional flags
    if '--preview' in sys.argv:
        preview = True
    if '--debug' in sys.argv:
        debug = True

    print(f"Input List File: {input_list_file}")
    print(f"Source Directory: {source_directory}")
    print(f"Target Directory: {target_directory}")
    print(f"Preview Mode: {'ON' if preview else 'OFF'}")
    print(f"Debug Mode: {'ON' if debug else 'OFF'}")

    if not os.path.isfile(input_list_file):
        print(f"Error: The input file '{input_list_file}' does not exist.")
        sys.exit(1)

    if not os.path.isdir(source_directory):
        print(f"Error: The source directory '{source_directory}' does not exist.")
        sys.exit(1)

    if not os.path.isdir(target_directory):
        print(f"Error: The target directory '{target_directory}' does not exist.")
        sys.exit(1)

    # File paths for logging
    index_file = '_Index.txt'
    verify_script = '_verify.sh'
    failure_file = 'failure.txt'

    # Clear existing log files
    if not preview:
        open(index_file, 'w').close()  # Empty the file if it exists
        open(verify_script, 'w').close()  # Empty the file if it exists
        open(failure_file, 'w').close()  # Empty the file if it exists

    extensions = read_extensions_from_file(input_list_file)
    move_files_by_extension(source_directory, target_directory, extensions, index_file, verify_script, failure_file, preview, debug)

if __name__ == "__main__":
    main()
