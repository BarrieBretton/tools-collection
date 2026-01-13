
import rich
import pathlib
import bcrypt
import hashlib
import threading
import errno

from hashlib import md5
from Crypto.Cipher import AES
from os import path, remove, urandom, listdir, walk

# Drop-in replacement for built-in 'multiprocessing' module is the 'multiprocess' module from PyPI
from multiprocess import Process

# -- Set by user -- #

# Created using the gen_pass function
# DB_ENC_PASS = b'$2b$12$lm9Jd6UtVKHcYwBKiIBHqO2GZyO6j.JD1zxFsJllRxgY8ko0mrDGu'
DB_ENC_PASS = b'$2a$12$sKrNcLwgR/mnUWb6EIGRuub56Zld9C.xmujaXA.3s7JMHQ8vbTbRC'

# Extensions to look for
EXTS = (".jpg", ".webp", ".png", ".bmp", ".jpeg", ".webp")

# -- Function Definitions -- #

def flatten(l):
    output = [] 

    # function used for remove nested
    # lists/tuples in python using recursion
    def r_nests(l):
        for i in l:
            if type(i) in (tuple, list):
                r_nests(i)
            else:
                output.append(i)

    r_nests(l)
    return output

class AESCipher(object):

    def __init__(self, pwd):
        self.password = pwd

    def newpath(self, x):
        return path.join(path.split(x)[0], path.split(x)[1]+".enc")

    def derive_key_and_iv(self, password, salt, key_length, iv_length): #derive key and IV from password and salt.
        d = d_i = b''
        while len(d) < key_length + iv_length:
            d_i = md5(d_i + str.encode(password) + salt).digest() #obtain the md5 hash value
            d += d_i
        return d[:key_length], d[key_length:key_length+iv_length]
    
    def encrypt(self, in_file, out_file, password, key_length=32):
        bs = AES.block_size #16 bytes
        salt = urandom(bs) #return a string of random bytes
        key, iv = self.derive_key_and_iv(password, salt, key_length, bs)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        out_file.write(salt)
        finished = False
    
        while not finished:
            chunk = in_file.read(1024 * bs) 
            if len(chunk) == 0 or len(chunk) % bs != 0: #final block/chunk is padded before encryption
                padding_length = (bs - len(chunk) % bs) or bs
                chunk += str.encode(padding_length * chr(padding_length))
                finished = True
            out_file.write(cipher.encrypt(chunk))
    
    def decrypt(self, in_file, out_file, password, key_length=32):
        bs = AES.block_size
        salt = in_file.read(bs)
        key, iv = self.derive_key_and_iv(password, salt, key_length, bs)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        next_chunk = ''
        finished = False
        while not finished:
            chunk, next_chunk = next_chunk, cipher.decrypt(in_file.read(1024 * bs))
            if len(next_chunk) == 0:
                padding_length = chunk[-1]
                chunk = chunk[:-padding_length]
                finished = True 
            out_file.write(bytes(x for x in chunk)) 
    

def file_enc(fpath, pwd, replace=True, display=False):
    aesc = AESCipher(pwd)
    
    if not pwd_auth(pwd): return 1
    if not path.exists(fpath):
        print(fpath)
        return 2

    try:
        with open(fpath, 'rb') as inf, open(fpath+'.enc', 'wb') as outf:
            try: aesc.encrypt(inf, outf, pwd)
            except Exception: return 3 
    except OSError as oserr:
        # Catch file name too long error
        if oserr.errno == errno.ENAMETOOLONG:
            rich.print(f"[red]FAILED[/red] [blue](Name Too Long)[/blue]: {fpath}")
        else:
            rich.print(f"[red]FAILED[/red] [blue]({oserr})[/blue]: {fpath}")

    if replace:
        try: remove(fpath)
        except Exception: pass

    if display: rich.print(f"[green]Successfully encrypted[/green]: {fpath}")
    return 0

def file_dec(fpath, pwd, replace=True, display=False):
    aesc = AESCipher(pwd)

    if not pwd_auth(pwd): return 1
    if not path.exists(fpath): return 2

    try:
        with open(fpath, 'rb') as inf, open(fpath.rstrip('.enc'), 'wb') as outf:
            try: aesc.decrypt(inf, outf, pwd)
            except Exception: return 3
    except OSError as oserr:
        # Catch file name too long error
        if oserr.errno == errno.ENAMETOOLONG:
            rich.print(f"[red]FAILED[/red] [blue](Name Too Long)[/blue]: {fpath}")
        else:
            rich.print(f"[red]FAILED[/red] [blue]({oserr})[/blue]: {fpath}")

    if replace:
        try: remove(fpath)
        except Exception: pass

    if display: rich.print(f"[green]Successfully decrypted[/green]: {fpath}")
    return 0


def use_pass(pwd):
    global DB_ENC_PASS
    DB_ENC_PASS = gen_hash(pwd).encode()

def all_files(dpath, exts=""):
    # dpath is path of main parent directory
    # exts must be a tuple of required extensions in lowercase

    # hidden linux files are also caught with this method
    # only a lazy generator object for files is returned by this functon

    # when 'exts' is left as empty, all files within dpath are recursively iterated
    all_files = (path.join(d, x)
                 for d, dirs, files in walk(dpath)
                 for x in files if x.lower().endswith(exts))
    return all_files

def secure_dir(dpaths,
               pwd,
               enc=False,
               recurse = False,
               exts = EXTS,
               dry_run=True,
               quiet=True,
               get_times=True,
               use_mp=False,
               auto_fast=True):

    if not pwd_auth(pwd): return 1

    for dpath in dpaths:
        if not path.exists(dpath): return 2

    # Take care of recurse condition

    if auto_fast:
        print("Using auto settings for best performance")
    else:
        if use_mp:
            print("Using multi-processing\n")
        else:
            print("Using multi-threading\n")

    if get_times:
        import time
        start_time = time.time()

    global files, sec_dir_procs

    files = []
    for dpath in dpaths:
        if recurse:
            # old method (does not catch hidden linux files)
            # files.extend(glob.iglob(f'{dpath}/**/*', recursive=True))

            # new method (catch hidden linux files)
            files.extend(all_files(dpath, ))
        else:
            files.extend([path.join(dpath, i) for i in listdir(dpath)])

    if enc:
        files = [i for i in files if i.endswith(tuple(exts))]
    else:
        files = [i for i in files if i.endswith('.enc')]

    tot = len(files)
    sec_dir_procs = []

    for ind, file in enumerate(files):
        if dry_run:
            if not quiet:
                print(f"{file} will be {['de', 'en'][enc]}crypted [{ind+1} of {tot} items/files]")
        else:
            if enc:
                # auto_fast always gets more preference, so MT is used for enc if auto_fast enabled
                if use_mp and not auto_fast:
                    sd_t = Process(target=lambda: file_enc(file, pwd, display = not quiet))
                else:
                    sd_t = threading.Thread(target=lambda: file_enc(file, pwd, display = not quiet))

            else:
                # auto_fast always gets more preference, so MP is used for dec if auto_fast enabled
                if use_mp or auto_fast:
                    sd_t = Process(target=lambda: file_dec(file, pwd, display = not quiet))
                else:
                    sd_t = threading.Thread(target=lambda: file_dec(file, pwd, display = not quiet))

            sec_dir_procs.append(sd_t)
            sd_t.start()

    for i in sec_dir_procs:
        i.join()

    if get_times:
        print(f"Time taken: {time.time() - start_time}")

    return 0

def pwd_auth(pwd):
    return verify_pass(pwd, DB_ENC_PASS)

def gen_hash(password):
    # Hashing the password
    phash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return phash

def verify_pass(userpassword, phash):
    # Taking user entered password
    result = bcrypt.checkpw(userpassword.encode('utf-8'), phash)  
    return result

# The following line is harmless and acts as a test parent dir (dpaths)
dpaths = [r"/media/vivojay/VIVOSANDISK/VIVAN/test"]

