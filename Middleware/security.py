import jwt
from Context.Context import Context
from time import time

_context = Context.get_default_context()

_protected_data = ['PUT:/api/user']

def hash_password(pwd):
    global _context
    h = jwt.encode(pwd, key=_context.get_context("JWT_SECRET"))
    # h = str(h)
    return h


def generate_token(info):

    info["timestamp"] =  time()
    email = info['email']

    if email == 'dff9@columbia.edu':
        info['role']='admin'
    else:
        info['role']='student'

    # info['created'] = str(info['created'])

    h = jwt.encode(info, key=_context.get_context("JWT_SECRET"))
    h = str(h)

    return h


def authorize(url, method, token):
    d = method + ':' + url
    if any(protected in d for protected in _protected_data):
        try:
            request_email = url.rsplit('/', 1)[1]
            token_email = jwt.decode(token, key=_context.get_context("JWT_SECRET"))['email']
            if request_email == token_email:
                return True
            return False
        except:
            return False
    else:
        return True
        # get token, case 1: admin can do anything case2: email == email for user can do it



