import os, hashlib

def user_construct(count : int):
    login = "SupEmployee{}".format(count+1)
    print(login)
    salt = os.urandom(16)
    hashed_password = hashlib.sha256(salt + os.urandom(10)).hexdigest()
    return login, hashed_password, salt
