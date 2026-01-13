from functools import partial
from itertools import repeat

import os
import sys
import json
import shutil
import rarfile
import zipfile
import py7zr
import multiprocess

OG_path = r"D:\DEMO\OG"
unsuccessful_exts = [0, 0, 0]

def un_arcs(dir_path):
    files = os.listdir(dir_path)

    zips = [i for i in files if i.endswith(".zip")]
    rars = [i for i in files if i.endswith(".rar")]
    sevenzips = [i for i in files if i.endswith(".7z")]

    left_zips = [os.path.join(dir_path, i) for i in zips if i.rstrip(".zip") not in files]
    left_rars = [os.path.join(dir_path, i) for i in rars if i.rstrip(".rar") not in files]
    left_sevenzips = [os.path.join(dir_path, i) for i in sevenzips if i.rstrip(".7z") not in files]

    return [left_zips, left_rars, left_sevenzips]

def refresh_status(arc_type):
    global unsuccessful_exts
    unsuccessful_exts[arc_type] += 1

def extract_zip(filename, extract_dir, dry_run=1):
    if dry_run:
        print(f"zip extraction: {filename} -> {extract_dir}")
        return
    try:
        with contextlib.supress(FileExistsError):
            os.mkdir(os.path.splitext(filename)[0])
        with zipfile.ZipFile(filename, 'r') as z:
            z.extractall(os.path.join(extract_dir, os.path.splitext(filename)[0]))
    except Exception as e:
        print(f"Exception while extracting zip file \"{filename}\", {e}")
        refresh_status(1)

def extract_sevenzip(filename, extract_dir, dry_run=1):
    if dry_run:
        print(f"7z extraction: {filename} -> {extract_dir}")
        return
    try:
        with contextlib.supress(FileExistsError):
            os.mkdir(os.path.splitext(filename)[0])
        with py7zr.SevenZipFile(filename, mode='r') as z:
            z.extractall(os.path.join(extract_dir, os.path.splitext(filename)[0]))
    except Exception as e:
        print(f"Exception while extracting 7z file \"{filename}\", {e}")
        refresh_status(1)

def extract_rar(filename, extract_dir, dry_run=1):
    if dry_run:
        print(f"rar extraction: {filename} -> {extract_dir}")
        return
    try:
        print(f"Extracting rar \"{filename}\"")
        with contextlib.supress(FileExistsError):
            os.mkdir(os.path.splitext(filename)[0])
        Archive = rarfile.RarFile(filename)
        Archive.extractall(os.path.join(extract_dir, os.path.splitext(filename)[0]))
    except Exception as e:
        print(f"Exception while extracting rar file \"{filename}\", {e}")
        refresh_status(1)

def convert_arcs(paths, extract_dir, dry_run=1):
    procs = []

    archive_extraction_functions = [extract_zip, extract_rar, extract_sevenzip]
    file_types = "zip rar 7z".split()

    # unarchiving files
    for paths, ex_func, f_t in zip(paths, archive_extraction_functions, file_types):
        print(f"{f_t}s")
        for i in paths:
            print("  > "+i)

            p = multiprocess.Process(target=ex_func, args=(i, extract_dir, dry_run))
            procs.append(p)
            p.start()

        print()

    print(json.dumps(unsuccessful_exts, indent=2))

if __name__ == "__main__":
    if len(sys.argv) == 1:
        remaining_files = un_arcs(OG_path)
    else:
        remaining_files = un_arcs(sys.argv[1])

    input("Hit enter to run async multiprocess pool: ")
    convert_arcs(remaining_files, OG_path, 0)


