# To check if file names within a given directory also exist in a list of directories
import os
import sys
import json
import bisect
import shutil
import itertools

from PIL import Image

EXTENSIONS = ['.png', '.bmp', '.jpg', '.jpeg', '.tiff', '.heic', '.raw', '.gif', '.pdf', '.eps', '.ai', '.psd', '.indd']

SAMPLE_INFO = {
    "ifp": r"D:\OneDrive - Suncity School\My Stuff\Pictures\__past__\parenthood\png_files",
    "ifds": [r"E:\VIVAN\personal\__past__\parenthood\png_files"],
}

SAMPLE_INFO = {
    "ifp": r"E:\VIVAN\test",
    "ifds": [r"E:\VIVAN\test\oth"],
}

def print_help():
    help_msg = """-h: Show this hekp and exit
-s: Use sample data

Use without arguments to initiate wizard
1 argument: the source directory path
2 arguments: list of comparison directory paths

"""
    print(help_msg)

def get_subdir_files(parent_dir, extensions):
    subdirectories = {}
    # for dirpath, dirnames, filename in os.walk(parent_dir):
    for dirpath, dirnames, _ in os.walk(parent_dir):
        subdirs = {}
        for dirname in dirnames:
            subdirpath = os.path.join(dirpath, dirname)
            filelist = []
            for filename in os.listdir(subdirpath):
                if filename.endswith(tuple(extensions)):
                    filelist.append(filename)
            filelist.sort()
            subdirs[dirname] = filelist
            # subdirs['.'] = sorted([i for i in os.listdir(subdirpath) if os.path.join(subdirpath, i)])
        subdirectories[dirpath] = subdirs
    return subdirectories

def get_res(image_path):
    # Open the image file
    with Image.open(image_path) as img:
        # Get the width and height of the image in pixels
        width, height = img.size
        # Get the physical size of the image in inches
        xres, yres = img.info.get('dpi', (None, None))
        if xres and yres:
            # Calculate the resolution in pixels per inch (PPI)
            xres_ppi = int(round(width / float(xres)))
            yres_ppi = int(round(height / float(yres)))

            return xres_ppi, yres_ppi
        else:
            print('Image resolution not found in metadata.')
            return 1

def get_dim(image_path):
    # Open the image file
    with Image.open(image_path) as img:
        # Get the width and height of the image in pixels
        return img.size

"""
def copy_dir_tree(src_base_dir, dest_base_dir, file_paths):
    # List of file paths to be copied `file_paths`

    # Iterate through each file path and copy to the destination directory
    for file_path in file_paths:
        # Get the relative path of the file with respect to the base directory
        rel_path = os.path.relpath(file_path, src_base_dir)

        # Construct the new file path in the destination directory
        dest_path = os.path.join(dest_base_dir, rel_path)

        # Create any missing directories in the destination path
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        # Copy the file to the new directory
        shutil.copy2(file_path, dest_path)
"""

def image_diff(path1, path2):
    import imagehash

    with Image.open(path1) as img1, Image.open(path2) as img2:
        # Calculate the hash values of the images using the average hash algorithm
        hash1 = imagehash.average_hash(img1)
        hash2 = imagehash.average_hash(img2)
        # Calculate the Hamming distance between the hash values
        distance = hash1 - hash2
        # Print the distance value
        return distance

def disp_dupes(dupes):
    for item, copies in dupes.items():
        print(item)
        for ind, copy in enumerate(copies):
            print(f" [{ind+1}] > {copy}\n")

def dupe_actions(dupes, action="keep-latest-ctime", discard_protocol="d"):
    discard_protocol = discard_protocol.lower()
    action = action.lower()
    print(action)

    actions = [
        "disc-matching-hashes",
        "disc-all-older-mtime",
        "disc-all-older-ctime",
        "keep-latest-mtime",
        "keep-latest-ctime",
        "keep-max-dim",
        "keep-max-res",
    ]

    if action in actions:
        # Discard Protocols
        # r -> remove discarded items
        # i -> isolate/move discarded items to another dir
        # d -> display discarded items

        # Invalid discard protocol, abort
        if discard_protocol not in ["r", "i", "d"]:
            print("Invalid discard protocol, aborting action")
            return 1

        # Both parameters are valid, continue with the action
        print(f"selected action: {action}, discard protocol: {discard_protocol}")
        action = actions.index(action)

        discard_pile = []

        # if action == 0:
        #     print("Duplicate Count: {0}".format(len(dupes)))
        #     for i, j in dupes.items():
        #         print(i)
        #         for x in j:
        #             print(f" > {x}")

        if action == 0:
            print("This is a useless option, 'cause images are already known to be exact replicas in order to be counted as duplicatesin the first place lol..., aborting")
            return 1

        elif action == 1:
            for src, matches in dupes.items():
                older_mtime_matches = [match for match in matches if os.path.getmtime(match) < os.path.getmtime(src)]
                if older_mtime_matches: discard_pile.append((src, older_mtime_matches))
                else: discard_pile.append((src, [src]))

        elif action == 2:
            for src, matches in dupes.items():
                older_ctime_matches = [match for match in matches if os.path.getctime(match) < os.path.getctime(src)]
                if older_ctime_matches: discard_pile.append((src, older_ctime_matches))
                else: discard_pile.append((src, [src]))

        elif action == 3:
            for src, matches in dupes.items():
                newer_mtime_matches = [match for match in matches if os.path.getmtime(match) > os.path.getmtime(src)]
                if newer_ctime_matches:
                    newest_mtime_match = max(newer_mtime_matches, key=os.path.getmtime)
                    discarded_matches = [i for i in matches if i != newest_mtime_match]
                    if newer_mtime_matches: discard_pile.append((src, discarded_matches))
                    else: discard_pile.append((src, [src]))
                else: discard_pile.append((src, [src]))

        elif action == 4:
            for src, matches in dupes.items():
                newer_ctime_matches = [match for match in matches if os.path.getctime(match) > os.path.getctime(src)]
                if newer_ctime_matches:
                    newest_ctime_match = max(newer_ctime_matches, key=os.path.getctime)
                    discarded_matches = [i for i in matches if i != newest_ctime_match]
                    if discarded_matches: discard_pile.append((src, discarded_matches))
                    else: discard_pile.append((src, [src]))
                else: discard_pile.append((src, [src]))

        elif action == 5:
            for src, matches in dupes.items():
                dims = [(i, get_dim(i)) for i in [src]+matches]
                dims.sort(key=lambda x:x[1])
                discarded_matches = [x[0] for x in dims[:-1]] # Save last one (max resolution) and discard the rest
                discard_pile.append((src, discarded_matches))

        elif action == 6:
            for src, matches in dupes.items():
                resolutions = [(i, get_res(i)) for i in [src]+matches]
                resolutions.sort(key=lambda x:x[1])
                discarded_matches = [x[0] for x in resolutions[:-1]] # Save last one (max resolution) and discard the rest
                discard_pile.append((src, discarded_matches))

    else:
        # Invalid action, abort
        print("Invalid action, aborting")
        return 1

    print("Unneeded Duplicates have been segregated and collected")
    # print(discard_pile)

    if discard_protocol == "d":
        # TODO: Write a simple script for the following...
        disp_dupes(dupes)

    elif discard_protocol == "i":
        perm = input("Confirm isolation of dupes to another dir? ('y' to confirm, abort otherwise): ").lower().strip()
        if perm == 'y':
            iso_dir = input("Please enter dir path for isolation: ")
            for src_path, rejected_files in discard_pile:
                src_name = os.path.splitext(os.path.basename(src_path))[0]
                for i, rpath in enumerate(rejected_files):
                    dest_path = os.path.join(iso_dir, f"{src_name}_[{i+1}]")
                    shutil.move(rpath, dest_path)
        else:
            print("Aborted duplicate isolation phase...")

    else:
        perm = input("Confirm permanent deletion of dupes? ('y' to confirm, abort otherwise): ").lower().strip()
        if perm == 'y':
            for _, rejected_files in discard_pile:
                for rpath in rejected_files:
                    os.remove(rpath)
        else:
            print("Aborted duplicate deletion phase...")

    return 0

def duplicate_check(ifp, ifds):
    dupes_info = {}
    file_structure = {ifd: get_subdir_files(ifd, EXTENSIONS) for ifd in ifds}

    # Check for all dupes
    for tfile in (os.path.join(ifp, i) for i in os.listdir(ifp) if os.path.isfile(os.path.join(ifp, i))):
        test_file_name = os.path.basename(tfile)
        for ifd in file_structure:
            for sdir in file_structure[ifd]:
                for ssdir in file_structure[ifd][sdir]:
                    files = file_structure[ifd][sdir][ssdir]
                    index = bisect.bisect_left(files, test_file_name)
                    if index != len(files) and files[index] == test_file_name:
                        saved_matches = dupes_info.get(os.path.abspath(tfile))
                        if saved_matches is None:
                            # Create a fresh match if no saved one is found
                            dupes_info[os.path.abspath(tfile)] = [(ifd, sdir, ssdir, index)]
                        else:
                            # Renew the saved match if found
                            dupes_info[os.path.abspath(tfile)].append((ifd, sdir, ssdir, index))

    files = []
    for dupe in dupes_info.items():
        src, matches = dupe

        dnames = [os.path.join(*match[1:3]) for match in matches]
        fnames = [file_structure[matches[x][0]][matches[x][1]][matches[x][2]][matches[x][3]] for x in range(len(matches))]

        files.extend([(src, os.path.join(dname, fname)) for dname, fname in zip(dnames, fnames)])

    files.sort(key=lambda x:x[0]) # Sort based on first element of each tuple entry
    groups = itertools.groupby(files, key=lambda x: x[0])

    files = {k: [v[1] for v in group] for k, group in groups}
    return files

def validate_directories(ifds):
    ifds = [ifd for ifd in ifds if os.path.isdir(ifd)]
    if ifds == []: return 1
    return ifds

def ask_for_ifp():
    ifp = input("Please enter abs path of source directory to check for duplicates: ")
    return ifp

def ask_for_directory():
    ifds = input("Please enter dir paths to check\n for comparisons to be made in (comma [,] separated): ")
    ifds.replace(', ', ',')
    ifds = ifds.split(',')
    if not isinstance(ifds, list):
        ifds = [ifds]
    return validate_directories(ifds)

def process_parameters(ifp, ifds):
    print(f"Source dir to check: {ifp}")
    if ifds == 1:
        print("None of the entered directories exist, aborting...")
        return 1
    else: # Atleast one dir is valid
        print("Following directories will be checked for dupes:\n")
        for x, ifd in enumerate(ifds):
            print(f" [{x+1}]> {ifd}")
        print(f"{'-'*80}\n")

def main():
    global SAMPLE_INFO

    # Define `argc` as argument count
    argc = len(sys.argv)

    # Some special arguments
    if argc == 2:
        if sys.argv[1] == '-h':
            print_help()
            return 0
        if sys.argv[1] == '-s':
            print("Using sample data (as requested by user)")
            print(json.dumps(SAMPLE_INFO, indent=2))

            ifp = SAMPLE_INFO['ifp']
            ifds = SAMPLE_INFO['ifds']

            if not os.path.isdir(ifp):
                print(f"Could not find dir to check: {ifp}. Aborting")
                return 1

    elif argc == 3: # First arg needs to be dir, next needs to be a list of one or more directories
        # Set `ifp` to first arg
        # ifp = sys.argv[1]
        ifp = sys.argv[1]

        # Check for validity of dir provided as ifp
        if not os.path.isdir(ifp):
            print(f"Could not find dir to check: {ifp}. Aborting")
            return 1

        # Set ifds to list of all dirs provided as arguments 2 and onwards
        ifds = sys.argv[2:]

    else:
        # No arguments provided
        if argc == 1:
            print("No args entered, starting wizard")
            # Ask for ifp
            ifp = ask_for_ifp()

        # 1 argument provided
        elif argc == 2:
            # Set ifp to sys.argv[1]
            ifp = sys.argv[1]

        else: # No more arguments are allowed
            print("A maximum of 3 arguments are allowed. Aborting...")
            return 1

    if argc == 1 or (argc == 2 and sys.argv[1] != '-s'):
        # Check if enetered `ifp` path is valid and continue, abort otherwise
        if not os.path.isdir(ifp):
            print(f"Could not find dir to check: {ifp}. Aborting...")
            return 1

        # Ask for ifds and
        ifds = ask_for_directory()

    # Perform Validation Checks on list of directories (`ifds`)
    ifds = validate_directories(ifds)

    # Process both params
    process_parameters(ifp, ifds)

    # Finally continue to initiate the main deduplication process
    return duplicate_check(ifp, ifds)

    # return 0


if __name__ == '__main__':
    # Driver Code
    main_returncode = main()
    # sys.exit(main_returncode)

# TODO: rm all lines below

"""
ifp, ifds = SAMPLE_INFO.values()
file_structure = {ifd: get_subdir_files(ifd, EXTENSIONS) for ifd in ifds}
fs = file_structure
dupes = duplicate_check(ifp, ifds)

print(json.dumps(fs['E:\\VIVAN\\test\\oth'], indent=2))

a=main_returncode
dupe_actions(a, "keep-max-dim", "r")

path1 = r"E:\VIVAN\personal\tmp"
path2 = r"E:\VIVAN\personal\__past__\parenthood"
a = duplicate_check(path1, [path2])
dupe_actions(a)
"""


