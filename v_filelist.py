
import os
from pathlib import Path

import pathspec

def get_files_according_to_gitignore(root_dir, gitignore_path='.gitignore'):
    # Load .gitignore rules
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as fh:
            spec = pathspec.PathSpec.from_lines('gitwildmatch', fh)
    else:
        spec = pathspec.PathSpec.from_lines('gitwildmatch', [])

    included_files = []
    for root, dirs, files in os.walk(root_dir):
        # Filter directories in-place to avoid walking ignored folders
        dirs[:] = [d for d in dirs if not spec.match_file(os.path.join(root, d))]

        for file in files:
            file_path = os.path.join(root, file)
            # Check if file is ignored
            if not spec.match_file(file_path):
                included_files.append(file_path)

    return included_files




def get_target_files(directory_path: str, extensions: list = ['.md', '.txt', '.log']) -> list[str]:
    """
    Scans a directory and returns a list of absolute paths for valid text files.
    """
    print(f"[Scavenger] Scanning {directory_path}...")
    target_files = []

    # Resolve converts a relative path (./) to an absolute path (/home/za/...)
    base_dir = Path(directory_path).resolve()

    if not base_dir.exists():
        print(f"Warning: Directory {base_dir} not found!")
        return target_files

    # rglob('*') recursively searches all folders and subfolders
    for filepath in base_dir.rglob('*'):
        if filepath.is_file() and filepath.suffix in extensions:
            target_files.append(str(filepath))

    print(f"[Scavenger] Found {len(target_files)} files ready for the bunker.")
    return target_files

file_list_str ="""
01-network-manager-all.yaml   clean_text.txt            grub                  oolisttmp.sh
970772112453073646367000.txt  day2                      helpoc                oolisttmp.yaml
Dockerfile                                         helpollama            package.info.txt
GEMINI.md                     docker.list                            red-bashrc
LlmManager.kt                 draft24apr                http-proxy.conf       rust.vs.cpp.md
a.dockerfile                  draft28apr.md             ip.addr.txt           rustGuess
agents.debug                                    kt.braindump.kt       
apr15.md                      lcmake                

"""

def make_file_list_from_str(f_list_str: str, pwd: str ="./") -> list[str]:
    """
    make a list of absolute path, file names chopped from the f_list_str
    """
    # 1. Resolve the base directory to an absolute path (e.g., /home/za/...)
    base_path = Path(pwd).resolve()

    # 2. .split() automatically discards all chaotic spaces, tabs, and newlines
    filenames = f_list_str.split()

    # 3. Join the absolute base path with each filename
    absolute_paths = [str(base_path / fname) for fname in filenames]

    print(f"[Scavenger] Extracted {len(absolute_paths)} hardcoded files from string.")

    return absolute_paths

# This allows you to test the script directly from the terminal
if __name__ == "__main__":
    test_dir = "/my/tec/"
    #flist = get_target_files(test_dir)
    flist1 = get_files_according_to_gitignore(test_dir)
    flist2 = get_files_according_to_gitignore(test_dir, gitignore_path='vector.ignore')

    # choose files appeared in both flist1 and flist2
    #flist  = tuple(flist1 xor flist2) 
    #flist = flist2
    flist = flist1 if len(flist1) < len(flist2) else flist2

    tmp_dir = Path("~/tmp/").expanduser().resolve()



    print("\n--- Dry Run File List ---")
    for f in flist:
        print(f)
