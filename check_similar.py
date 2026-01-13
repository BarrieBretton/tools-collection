import os
import sys
import json
import imagehash

from PIL import Image

EXTENSIONS = [
    '.png',
    '.bmp',
    '.jpg',
    '.jpeg',
    '.tiff',
    '.heic',
    '.raw',
    '.gif',
    '.pdf',
    '.eps',
    '.ai',
    '.psd',
    '.indd',
]

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

def image_diff(path1, path2):
    with Image.open(path1) as img1, Image.open(path2) as img2:
        # Calculate the hash values of the images using the average hash algorithm
        hash1 = imagehash.average_hash(img1)
        hash2 = imagehash.average_hash(img2)
        # Calculate the Hamming distance between the hash values
        distance = hash1 - hash2
        # Print the distance value
        return distance

def validate_directories(ifds):
    ifds = [ifd for ifd in ifds if os.path.isdir(ifd)]
    if ifds == []: return 1
    return ifds

# actions = [
#     "disc-matching-hashes",
#     "disc-all-older-mtime",
#     "disc-all-older-ctime",
#     "keep-latest-mtime",
#     "keep-latest-ctime",
#     "keep-max-dim",
#     "keep-max-res",
# ]

def dupe_actions(dupes, action="keep-latest-ctime", discard_protocol="d"):
    discard_protocol = discard_protocol.lower()

    if action in range(7):
        # Discard Protocols
        # r -> remove discarded items
        # i -> isolate/move discarded items to another dir
        # d -> display discarded items

        # Invalid discard protocol, abort
        if discard_protocol not in ["r", "i", "d"]:
            print("Invalid discard protocol, aborting action")
            return 1

        # Both parameters are valid, continue with the action
        print(f"selected action: {action}; discard protocol: {discard_protocol}")

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
                newest_mtime_match = max(newer_mtime_matches, key=os.path.getmtime)
                discarded_matches = [i for i in matches if i != newest_mtime_match]
                if newer_mtime_matches: discard_pile.append((src, discarded_matches))
                else: discard_pile.append((src, [src]))

        elif action == 4:
            for src, matches in dupes.items():
                newer_ctime_matches = [match for match in matches if os.path.getctime(match) > os.path.getctime(src)]
                newest_ctime_match = max(newer_ctime_matches, key=os.path.getctime)
                discarded_matches = [i for i in matches if i != newest_ctime_match]
                if discarded_matches: discard_pile.append((src, discarded_matches))
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
    print(discard_pile)

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


def create_image_similarity_matrix(dir_path, display_progress=True, save_results_path=None):
    # Get list of all absolute file paths recursively within `dir_path`
    file_paths = []
    for root, _, files in os.walk(dir_path):
        for filename in files:
            file_path = os.path.abspath(os.path.join(root, filename))
            file_paths.append(file_path)

    image_diff_pairs = {}
    path_count = len(file_paths)

    for indi, i in enumerate(file_paths[:-1]):
        if display_progress: print(f"Tagging similarities of pairings of image {indi+1} of {path_count + 1} ", end="")

        image_diff_pairs[i] = []
        for j in range(indi+1, path_count):
            imgd = image_diff(file_paths[indi], file_paths[j])
            image_diff_pairs[i].append((imgd, file_paths[j]))
            if display_progress: print(f"(Processing Pair: [{j+1} of {path_count - j}])", end="")
        image_diff_pairs[i].sort(key=lambda x:x[0]) # Most similar first, images listed in decreasing order of similarity

    if display_progress: print(" "*80)

    if save_results_path is not None:
        with open(save_results_path, encoding="utf-8") as fp:
            json.dump(image_diff_pairs, fp)

    return image_diff_pairs

def filter_similar(image_similarity_matrix, include_similarity_value=False, thresh=0.96):
    maxdist = round((1-thresh)*100)
    results = {}
    for src_img, v in image_similarity_matrix.items():
        if include_similarity_value:
            res = [(dist, comp_img) for dist, comp_img in v if dist <= maxdist]
        else:
            res = [comp_img for dist, comp_img in v if dist <= maxdist]
        if src_img not in results and res: results[src_img] = []
        if res: results[src_img].extend(sorted(res))
    return results

def display_similar(src_dir, thresh):
    results = filter_similar(create_image_similarity_matrix(src_dir), thresh=thresh)
    print(json.dumps(results, indent=2))
    return results

def display_dupes(src_dir):
    return display_similar(src_dir, thresh=1)

if __name__ == "__main__":
    print("May also be sed as a module")
    try:
        src_dir = input("Enter src dir path: ")
        # thresh = float(input("Enter threshold value (b/w 0.0 and 1.0, 1.0 meaning exact match): "))
        # results = display_similar(src_dir, thresh)
        dupes = display_dupes(src_dir)

    except Exception:
        pass
    # sys.exit(0)



