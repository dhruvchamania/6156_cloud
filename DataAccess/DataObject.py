import DataAccess.DataAdaptor as data_adaptor
from abc import ABC, abstractmethod
import pymysql.err
from Middleware import notification

class DataException(Exception):

    unknown_error   =   1001
    duplicate_key   =   1002

    def __init__(self, code=unknown_error, msg="Something awful happened."):
        self.code = code
        self.msg = msg

class BaseDataObject(ABC):

    def __init__(self):
        pass

    @classmethod
    @abstractmethod
    def create_instance(cls, data):
        pass


class UsersRDB(BaseDataObject):

    def __init__(self, ctx):
        super().__init__()

        self._ctx = ctx

    @classmethod
    def get_by_email(cls, email):

        sql = "select * from baseball.users where email=%s"
        #sql = "update baseball.users set email= "
        res, data = data_adaptor.run_q(sql=sql, args=(email), fetch=True)
        if data is not None and len(data) > 0:
            result =  data[0]
        else:
            result = None

        return result

    @classmethod
    def get_by_query(cls, temp, cols):

        query = data_adaptor.create_select('baseball.users', template=temp, fields=cols)
        res, data = data_adaptor.run_q(sql=query[0], args=(query[1]), fetch=True)
        if data is not None and len(data) > 0:
            result =  data[0]
        else:
            result = None

        return result

    @classmethod
    def get_by_userid(cls, userid):

        sql = "select * from baseball.users where id=%s"
        # sql = "update baseball.users set email= "
        res, data = data_adaptor.run_q(sql=sql, args=(userid), fetch=True)
        if data is not None and len(data) > 0:
            result = data[0]
        else:
            result = None

        return result

    @classmethod
    def get_by_userid(cls, userid):

        sql = "select * from baseball.users where id=%s"
        # sql = "update baseball.users set email= "
        res, data = data_adaptor.run_q(sql=sql, args=(userid), fetch=True)
        if data is not None and len(data) > 0:
            result = data[0]
        else:
            result = None

        return result

    @classmethod
    def delete_by_email(cls, email):

        sql = "UPDATE baseball.users SET "
        sql = "delete from baseball.users where email=%s"
        res, data = data_adaptor.run_q(sql=sql, args=(email), fetch=True)
        if data is not None and len(data) > 0:
            result =  data[0]
        else:
            result = None

        return result

    @classmethod
    def create_user(cls, user_info):

        result = None

        try:
            sql, args = data_adaptor.create_insert(table_name="users", row=user_info)
            res, data = data_adaptor.run_q(sql, args)

            msg = {"customers_email": user_info['email']}
            notification.publish_it(msg)

            if res != 1:
                result = None
            else:
                result = user_info['id']
        except pymysql.err.IntegrityError as ie:
            if ie.args[0] == 1062:
                raise (DataException(DataException.duplicate_key))
            else:
                raise DataException()
        except Exception as e:
            raise DataException()

        return result

    @classmethod
    def update_user(cls, email, data):
        result = None

        try:
            sql, args = data_adaptor.create_update(table_name="baseball.users",new_values=data,template={"email":email})
            res, data = data_adaptor.run_q(sql, args)
            if data is not None and len(data) > 0:
                result = data[0]
            else:
                result = None
        except pymysql.err.IntegrityError as ie:
            if ie.args[0] == 1062:
                raise (DataException(DataException.duplicate_key))
            else:
                raise DataException()
        except Exception as e:
            raise DataException()

        return result

    @classmethod
    def delete_user(cls, user_info):

        result = None

        try:
            sql, args = data_adaptor.create_update(table_name="users", new_values = {"status":"DELETED"}, template = {"email": user_info["email"]})
            res, data = data_adaptor.run_q(sql, args)
            if data is not None and len(data) > 0:
                result = data[0]
            else:
                result = None
        except pymysql.err.IntegrityError as ie:
            if ie.args[0] == 1062:
                raise (DataException(DataException.duplicate_key))
            else:
                raise DataException()
        except Exception as e:
            raise DataException()

        return result






