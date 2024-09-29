import os
import sys

def get_unique_file_extensions(start_dir):
    # Set to store unique file extensions
    unique_extensions = set()

    # Walk through the directory recursively
    for root, dirs, files in os.walk(start_dir, followlinks=False):
        for file in files:
            # Split the file name to get the extension
            _, extension = os.path.splitext(file)
            if extension:  # Ignore files without extensions
                unique_extensions.add(extension)

    return unique_extensions

def write_extensions_to_file(extensions):
    # Define the output file path in the current directory
    output_file = os.path.join(os.getcwd(), 'fileTypes.dat')

    # Write the unique extensions to the file
    with open(output_file, 'w') as f:
        for ext in sorted(extensions):
            f.write(f"{ext}\n")

def main():
    # Check if the start directory is passed as a command line argument
    if len(sys.argv) != 2:
        print("Usage: python script.py <start_directory>")
        sys.exit(1)

    start_dir = sys.argv[1]

    # Check if the start directory exists
    if not os.path.isdir(start_dir):
        print(f"Error: The directory '{start_dir}' does not exist.")
        sys.exit(1)

    # Get unique file extensions
    unique_extensions = get_unique_file_extensions(start_dir)

    # Write extensions to the file in the current directory
    write_extensions_to_file(unique_extensions)

    print(f"Unique file extensions have been written to {os.path.join(os.getcwd(), 'fileTypes.dat')}")

if __name__ == "__main__":
    main()
