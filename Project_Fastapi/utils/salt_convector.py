import base64

def from_json(salt):
    return base64.b64decode(salt)


def to_json(salt):
    return base64.b64encode(salt).decode('utf-8'),