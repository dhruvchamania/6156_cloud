from abc import ABC, abstractmethod
from Context.Context import Context
from DataAccess.DataObject import UsersRDB as UsersRDB
import uuid

# The base classes would not be IN the project. They would be in a separate included package.
# They would also do some things.
from Middleware import security


class ServiceException(Exception):

    unknown_error   =   9001
    missing_field   =   9002
    bad_data        =   9003

    def __init__(self, code=unknown_error, msg="Oh Dear!"):
        self.code = code
        self.msg = msg


class BaseService():

    missing_field   =   2001

    def __init__(self):
        pass


class UsersService(BaseService):

    required_create_fields = ['last_name', 'first_name', 'email', 'password']

    def __init__(self, ctx=None):

        if ctx is None:
            ctx = Context.get_default_context()

        self._ctx = ctx


    @classmethod
    def get_by_email(cls, email):

        result = UsersRDB.get_by_email(email)
        return result

    @classmethod
    def delete_user(cls, user_info):
        result = UsersRDB.delete_user(user_info = user_info)
        return result

    @classmethod
    def update_user(cls, email, data):
        # hash password before updating
        if 'password' in data:
            data['password'] = security.hash_password({"password" : data['password']})
        if 'status' in data:
            print('updating status to', data['status'])
        result = UsersRDB.update_user(email=email, data=data)
        return result

    @classmethod
    def create_user(cls, user_info):
        for f in UsersService.required_create_fields:
            v = user_info.get(f, None)
            if v is None:
                raise ServiceException(ServiceException.missing_field,
                                       "Missing field = " + f)

            if f == 'email':
                if v.find('@') == -1:
                    raise ServiceException(ServiceException.bad_data,
                           "Email looks invalid: " + v)

        user_info['id'] = str(uuid.uuid4())
        result = UsersRDB.create_user(user_info=user_info)

        return result





