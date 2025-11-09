import glob
import os


def count_lines_in_directory(directory):
    """Count lines in all Python files in the directory."""
    total_lines = 0
    file_counts = []

    for py_file in glob.glob(os.path.join(directory, "**", "*.py"), recursive=True):
        try:
            with open(py_file, encoding='utf-8') as f:
                lines = len(f.readlines())
                total_lines += lines
                file_counts.append((py_file, lines))
        except Exception as e:
            print(f"Error reading {py_file}: {e}")

    return total_lines, file_counts

if __name__ == "__main__":
    directory = "."  # Current directory
    total_lines, file_counts = count_lines_in_directory(directory)

    # Sort by line count, descending
    file_counts.sort(key=lambda x: x[1], reverse=True)

    print(f"Total lines of code: {total_lines}")
    print(f"Total Python files: {len(file_counts)}")
    print("\nTop 10 largest Python files:")
    for file_path, line_count in file_counts[:10]:
        print(f"  {line_count:6d} lines - {file_path}")

    # Write all file counts to file
    with open("file_sizes_baseline.txt", "w") as f:
        f.write(f"Total lines of code: {total_lines}\n")
        f.write(f"Total Python files: {len(file_counts)}\n")
        f.write("\nAll Python files sorted by line count:\n")
        for file_path, line_count in file_counts:
            f.write(f"  {line_count:6d} lines - {file_path}\n")
