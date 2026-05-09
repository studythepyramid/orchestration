import subprocess
import os

def is_text_file_subp(filepath: str) -> bool:
    """
    Checks if a file is a text file on Ubuntu using the 'file' command.

    Args:
        filepath: The path to the file to check.

    Returns:
        True if the file is determined to be a text file, False otherwise.
    """
    # First, ensure the path points to an actual file.
    if not os.path.isfile(filepath):
        return False

    try:
        # Execute the 'file --mime-encoding' command.
        # 'check=True' ensures that a CalledProcessError is raised 
        # if the command returns a non-zero exit code.
        # 'capture_output=True' captures stdout and stderr.
        # 'text=True' decodes stdout/stderr as text, making them strings.
        result = subprocess.run(
            ['file', '--mime-encoding', filepath],
            capture_output=True,
            text=True,
            check=True
        )
        
        # The output format is typically like: '/path/to/file: encoding'
        # We need to parse this to get the actual encoding.
        output_lines = result.stdout.strip().split(' ')
        if not output_lines:
            # This case is unlikely if check=True, but defensive programming is good.
            return False 

        # The encoding is the last part after the colon and space.
        # Example: '/home/user/document.txt: utf-8'
        mime_encoding = output_lines[-1].split(': ')[-1].strip()

        # If the detected encoding is 'binary', we assume it's not a text file.
        # Otherwise, we consider it a text file.
        return mime_encoding != 'binary'

    except FileNotFoundError:
        # This exception occurs if the 'file' command is not found on the system.
        # It's rare on Ubuntu but important to handle.
        print("Error: 'file' command not found. Please ensure it is installed and in your PATH.")
        return False
    except subprocess.CalledProcessError as e:
        # This handles errors reported by the 'file' command itself,
        # e.g., permission denied for the file.
        print(f"Error executing 'file' command for '{filepath}': {e.stderr.strip()}")
        return False
    except Exception as e:
        # A catch-all for any other unexpected issues.
        print(f"An unexpected error occurred while checking '{filepath}': {e}")
        return False

# Example usage:
# Replace 'path/to/your/text_file.txt' and 'path/to/your/binary_file.jpg'
# with actual file paths on your system for testing.

# For example, if you have 'a.py' and 'README.md' in the current directory,
# you could test with:
# print(f"'a.py' is text: {is_text_file_subp('a.py')}")
# print(f"'README.md' is text: {is_text_file_subp('README.md')}")
# print(f"'non_existent_file.xyz' is text: {is_text_file_subp('non_existent_file.xyz')}")


def is_text_file(filepath: str, chunk_size: int = 1024) -> bool:
    """
    Attempts to determine if a file is a text file using heuristics
    by trying to decode a chunk of its content as UTF-8.

    This method is a heuristic and may not be 100% accurate for all file types.
    It assumes that text files are primarily UTF-8 encoded.

    Args:
        filepath: The path to the file to check.
        chunk_size: The number of bytes to read from the beginning of the file
                    to make the determination.

    Returns:
        True if the file is likely a text file, False otherwise.
    """
    # Ensure the path points to an actual file.
    if not os.path.isfile(filepath):
        return False

    # An empty file is generally considered a text file.
    if os.path.getsize(filepath) == 0:
        return True

    try:
        with open(filepath, 'rb') as f:
            # Read a portion of the file. A larger chunk increases accuracy but
            # also cost for very large files. 1024 bytes is usually sufficient
            # to detect binary content early.
            chunk = f.read(chunk_size)

        # Attempt to decode the chunk as UTF-8. If this succeeds, it's very likely text.
        # If it fails with a UnicodeDecodeError, it's likely binary.
        chunk.decode('utf-8')
        return True
    except UnicodeDecodeError:
        # The chunk could not be decoded as UTF-8, suggesting it's binary.
        return False
    except Exception as e:
        # Handle other potential errors like permission denied.
        # print(f"An error occurred while checking '{filepath}': {e}") # Optional: log the error
        return False


