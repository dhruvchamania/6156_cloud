import copy

import os
import json

class Context():

    _app_context = None
    _application_name = None


    def __init__(self, inital_ctx=None):

        self._context = inital_ctx


    def get_context(self, ctx_name):

        result = self._context.get(ctx_name, None)
        return result

    def set_context(self, ctx_name, ctx):

        self._context[ctx_name] = copy.deepcopy(ctx)

    @classmethod
    def set_application_name(cls, application_name):
        cls._application_name = application_name
    
    
    @classmethod
    def get_default_context(cls):

        db_connect_info = os.environ.get('db_connect_info', None)
        if db_connect_info is not None:
            db_connect_info = json.loads(db_connect_info)
        else:
            db_connect_info = None

        JWT_SECRET = os.environ.get('JWT_SECRET', None)

        ctx = { "db_connect_info": db_connect_info,
                "JWT_SECRET": JWT_SECRET}
        result = Context(ctx)
        return result
