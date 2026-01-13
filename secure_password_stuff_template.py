from typing import Tuple
import os
import hashlib
import hmac
import yaml

with open("passstore.yml", 'r') as stream: # File that stores the password and salt in sha256 format
    try:
        truePass=(yaml.safe_load(stream))
    except yaml.YAMLError as exc:
        print(exc)

def is_correct_password(salt: bytes, pw_hash: bytes, password: str) -> bool:
    """
    Given a previously-stored salt and hash, and a password provided by a user
    trying to log in, check whether the password is correct.
    """
    return hmac.compare_digest(
        pw_hash,
        hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    )


if __name__ == '__main__':
	userInputPass=input('Enter password: ')

    if is_correct_password(truePass['SALT'], truePass['PW_HASH'], userInputPass): # Password is correct
		# code...
		pass
    else:
		# code...
		pass

# code...