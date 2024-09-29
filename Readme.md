# File Management and Logging Script

This Python script automates the process of moving files from a source directory to a target directory based on file extensions specified in a list. The script also logs the operations performed (file moves, deletions, failures) and provides robust error handling. Files are organized in the target directory by their creation date, ensuring a clear and chronological folder structure.

## Features:
- **File Movement**: Moves files from the source to the target directory based on their extensions.
- **Directory Organization**: Organizes files in the target directory by their creation date (`YYYY/MM/DD`).
- **Logging**: Logs all file operations (`_Index.txt`, `_verify.sh`, `failure.txt`) in a user-specified or default log directory.
- **Backup of Logs**: Backs up existing log files with a timestamp before appending new data.
- **Preview Mode**: Allows you to preview the actions without making any actual changes.
- **Debug Mode**: Provides detailed output of the operations performed.

## Prerequisites

- Python 3.x
- The `shutil` module for file handling (bundled with Python)
- Permission to read/write to source/target directories and log directories.

## Usage

```bash
python script.py <inputListFile> <SourceDirectory> <TargetDirectory> [--preview] [--debug] [--logdir <log_directory>]
```

### Arguments:

- `<inputListFile>`: The path to a file containing a list of file extensions (one per line) to be processed.
- `<SourceDirectory>`: The directory from which files will be moved.
- `<TargetDirectory>`: The directory where files will be moved to.
- `--preview` (optional): If specified, the script will display what actions it would take without making any actual changes.
- `--debug` (optional): Enables verbose output with detailed information about directories and files being processed.
- `--logdir <log_directory>` (optional): Specifies a custom directory for logging files. If not provided, it defaults to a `logs` subdirectory in the current working directory.

### Example Usage

#### Basic Operation:
```bash
python script.py extensions.txt /path/to/source /path/to/target
```

This command:
- Reads file extensions from `extensions.txt`
- Moves files with those extensions from `/path/to/source` to `/path/to/target`
- Logs operations in the `logs` subdirectory

#### Specifying a Custom Log Directory:
```bash
python script.py extensions.txt /path/to/source /path/to/target --logdir /custom/log/directory
```

This command:
- Performs the same file move as above but stores log files in `/custom/log/directory`.

#### Preview Mode:
```bash
python script.py extensions.txt /path/to/source /path/to/target --preview
```

This command:
- Shows which files would be moved and logged but does not actually move or log anything.

#### Debug Mode:
```bash
python script.py extensions.txt /path/to/source /path/to/target --debug
```

This command:
- Provides detailed output about the directories being scanned and the files being processed.

## Directory Structure of Moved Files

The script organizes files in the target directory by their **creation date**. Each file is placed in a directory corresponding to the year, month, and day of its creation.

### Directory Structure

The structure looks like this:

```
<target_directory>/<year>/<month>/<day>/
```

For example, if a file was created on **March 15, 2023**, and the target directory is `/path/to/target`, the file will be moved to:

```
/path/to/target/2023/03/15/
```

### Process for Organizing Files:

1. **File Creation Date**: The script reads the file's creation time using `os.stat(file_path).st_ctime` (or modification time if unavailable).
   
2. **Directory Creation**: The script formats the creation time into a path structured as `YYYY/MM/DD`, and if that directory does not exist, it creates the necessary subdirectories within the target directory.

3. **File Placement**: The file is then moved to the corresponding `YYYY/MM/DD` directory within the target directory.

### Example:

Suppose the source directory contains a file `report.pdf` created on **August 5, 2022**. If the target directory is `/data/backup`, the file will be moved to:

```
/data/backup/2022/08/05/report.pdf
```

The script creates the necessary subfolders (`/2022/08/05/`) if they do not already exist.

### Handling Duplicate Files

If a file with the same name already exists in the target folder, the script:
- **Calculates the hash** of both the source and target files.
- If the files are identical, the source file is deleted.
- If the files differ, the script generates a **new, incremental filename** to avoid overwriting the existing file. The new filename is in the format:

```
<filename>_<counter>.<extension>
```

For example, if `report.pdf` already exists, the script will rename the new file as `report_001.pdf`.

## Log Files

- **_Index.txt**: Contains a record of all files moved or deleted.
- **_verify.sh**: A shell script that lists all moved files for verification.
- **failure.txt**: Records any file operation errors, such as missing files, permission issues, or other failures.

### Log File Behavior:

1. **Default Log Location**: By default, log files are stored in the `logs` subdirectory of the current directory.
2. **Custom Log Location**: You can specify a custom log directory using the `--logdir` option.
3. **Backup of Existing Logs**: If any of the log files (`_Index.txt`, `_verify.sh`, or `failure.txt`) already exist, a backup will be created with a timestamp (format: `YYYYMMDD_HHMMSS.bak`), and new log data will append to the existing files.
4. **Error Handling**: If there are errors creating the log directory, backing up logs, or writing to log files, the script will exit with an appropriate error message.

### Example Log Entries

#### _Index.txt:
```
/path/to/source/file1.txt -> moved
/path/to/source/file2.txt -> deleted
```

#### _verify.sh:
```
ls -l '/path/to/target/file1.txt'
```

#### failure.txt:
```
Failure: Permission denied -> Source: /path/to/source/file3.txt
```

## Error Handling

- If any errors occur while creating the log directory, backing up logs, or writing to log files, the script will exit and provide an appropriate error message.
  
- If file operations (such as moving or deleting files) encounter errors, the failure will be logged in `failure.txt`, and the script will continue processing the remaining files.

## Extending the Script

The script can be easily extended by adding new logging functionalities, incorporating more file operations, or adding extra error handling mechanisms as needed.

## License

MIT License.