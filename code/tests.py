import hashlib
import binascii
import os


def hash_password(password):  # hashing the password and creating a salt (returning both)
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    password_hash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    password_hash = binascii.hexlify(password_hash)
    password_hash = password_hash.decode('ascii')
    salt = salt.decode('ascii')
    return password_hash, salt
    # End hash_password

print(hash_password('12345rs'))
