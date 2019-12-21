

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

    @classmethod
    def get_required_fields(cls):
        return cls.required_create_fields

    @classmethod
    def valid_create_fields(cls, new_value):
        req_fields = cls.get_required_fields()

        for f in req_fields:
            v = new_value.get(f, None)
            if v is None:
                raise ServiceException(ServiceException.missing_field,
                                       "Missing field = " + f)

        return True


