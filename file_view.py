import os
import sys
import glob
import subprocess as sp

from file_securer_vivo_multi_proc import file_enc, file_dec

def valid_fp(fp):
	l = [i for i in [fp, fp+'.enc', fp.rstrip('.enc')] if os.path.isfile(i)]
	if l == []: return ''
	return l[0]

def phelp():
    print("Usage:")
    print("Use without arguments to use as a wizard")
    print("1 arg: Must be file path")
    print("2 args: {1} must be file path, {2} must be pwd")

def main():
    pwd = 'maethebae'
    args = sys.argv[1:]

    print()

    if len(args) == 0:
        fps_ = input("Enter file path: ")
        fps = glob.glob(fps_)
        if fps == [] and fps_.strip():
            fps = [fps_]
        fps = [valid_fp(fp) for fp in fps]

        if not all(os.path.isfile(fp) for fp in fps):
            print("Invalid path(s), aborting")
            sys.exit(0)

        dpwd = pwd
        pwd = input("Leave empty to revert to default: ")
        if pwd.strip() == "":
            pwd = dpwd

    if len(args) == 1:
        if args[0] in ['-h', '--help']:
            phelp()
            sys.exit()

        fps_ = args[0]
        fps = glob.glob(fps_)
        if fps == [] and fps_.strip():
            fps = [fps_]

        fps = [valid_fp(fp) for fp in fps]
        if not all([os.path.isfile(fp) for fp in fps]):
            print("Invalid path, aborting")
            sys.exit(0)

    elif len(args) == 2:
        if not all([os.path.isfile(fp) for fp in fps]):
            print("Invalid path, aborting")
            sys.exit(0)

        if not args[1].isdigit():
            pwd = args[1]
        else:
            print("Invalid argument, expected password, aborting")
            sys.exit(0)


    for fp in fps:
        try:
            if fp.endswith('.enc'):
                a = file_dec(fp, pwd)
                if len(fps) == 1:
                    print("Unlocked file")
                if a == 1:
                    print("Incorrect password, aborting")
                    sys.exit(0)
                elif len(fps) == 1:
                    print(f"Viewing {os.path.split(fp)[1]}")

            sp.run(f"kitty +icat '{fp.rstrip('.enc')}'", shell=1)

            file_enc(fp.rstrip('.enc'), pwd)
            if len(fps) == 1:
                print("Locked file")

        except KeyboardInterrupt:
            while (True):
                try:
                    file_enc(fp.rstrip('.enc'), pwd)
                    print("Locked file")
                    sys.exit(0)
                except Exception:
                    pass

if __name__ == "__main__":
    main()


