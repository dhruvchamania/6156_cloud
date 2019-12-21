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
        

        local_db = '{"password":"dbuserdbuser","port":3306,"host":"e6156.csmcgds5qxyp.us-east-1.rds.amazonaws.com","user":"admin"}'
        #db_connect_info = os.environ.get('db_connect_info', None)
        db_connect_info = local_db 
        if db_connect_info is not None:
            db_connect_info = json.loads(db_connect_info)
        else:
            db_connect_info = None

        JWT_SECRET = os.environ.get('JWT_SECRET', None)

        ctx = { "db_connect_info": db_connect_info,
                "JWT_SECRET": JWT_SECRET}
        result = Context(ctx)
        return result
