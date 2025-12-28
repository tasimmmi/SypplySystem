import os
import hashlib
import string
import random
import base64

def user_construct():
    login = "SupEmployee"
    salt = os.urandom(16)
    password = generate_password(10)
    hashed_password = hashlib.sha256(salt + password.encode('utf-8')).hexdigest()
    user = {
        'login': login,
        'salt': base64.b64encode(salt).decode('utf-8'),
        'password': hashed_password
    }
    return user, password

def generate_password(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
