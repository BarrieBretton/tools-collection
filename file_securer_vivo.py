import glob
import bcrypt
import hashlib

from hashlib import md5
from Crypto.Cipher import AES
from os import path, remove, urandom

"""
class AESCipher(object):

    def __init__(self, key):
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode()))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

"""

# Set by user
DB_ENC_PASS = b'$2a$12$gG5qntksrtQqD83NXd3zPuSxDK0gMMKqTVpe8zzGo17DpNiGtts8G'
EXTS = (".jpg", ".webp", ".png", ".bmp", ".jpeg")

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
            if len(chunk) == 0 or len(chunk) % bs != 0:#final block/chunk is padded before encryption
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
    

def file_enc(fpath, pwd, replace=True):
    aesc = AESCipher(pwd)
    
    if not pwd_auth(pwd): return 1
    if not path.exists(fpath): return 2

    with open(fpath, 'rb') as inf, open(fpath+'.enc', 'wb') as outf:
        try:
            aesc.encrypt(inf, outf, pwd)
        except Exception:
            return 3 

    if replace:
        try:
            remove(fpath)
        except Exception:
            pass

    return 0

def file_dec(fpath, pwd, replace=True):
    aesc = AESCipher(pwd)

    if not pwd_auth(pwd): return 1
    if not path.exists(fpath): return 2

    with open(fpath, 'rb') as inf, open(fpath.rstrip('.enc'), 'wb') as outf:
        try:
            aesc.decrypt(inf, outf, pwd)
        except Exception:
            return 3

    if replace:
        try:
            remove(fpath)
        except Exception:
            pass

    return 0

def secure_dir(dpaths,
               pwd,
               enc=False,
               recurse = False,
               exts = EXTS,
               dry_run=True,
               quiet=True):

    if not pwd_auth(pwd): return 1

    for dpath in dpaths:
        if not path.exists(dpath): return 2

    # Take care of recurse condition
    files = []
    for dpath in dpaths:
        files.extend(glob.iglob(f'{dpath}/**/*', recursive=recurse))

    if enc:
        files = [i for i in files if i.endswith(exts)]
    else:
        files = [i for i in files if i.endswith('.enc')]

    tot = len(files)

    for ind, file in enumerate(files):
        if dry_run:
            if not quiet:
                print(f"{file} will be {['de', 'en'][enc]}crypted [{ind+1} of {tot} items/files]")
        else:
            if enc:
                if quiet:
                    file_enc(file, pwd)
                else:
                    print("  >", file_enc(file, pwd))
            else:
                if quiet:
                    file_dec(file, pwd)
                else:
                    print("  >", file_dec(file, pwd))
            try:
                remove(file)
            except Exception:
                pass

            if not quiet:
                print(f"Cur: {file} {['De', 'En'][enc]}crypted {ind+1} of {tot} items/files")

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


