import copy
import DataAccess.DataAdaptor as data_adaptor
from DataAccess.DataObject import BaseDataObject
from DataAccess.DataObject import DataException
import uuid
import pymysql


class ProfileRDB(BaseDataObject):


    @classmethod
    def _get_table_info(cls):

        info = {
            "table_name": "baseball.profile"
        }
        return info

    @classmethod
    def get_table_name(cls):
        t_info = cls._get_table_info()
        result = t_info['table_name']
        return result

    @classmethod
    def _process_result(cls, data):
        
        # Make sure data is either array or single dict obj

        result = {}
        result['userid'] = data[0]['userid']
        result['profileid'] = data[0]['profileid']
        result['elements'] = []

        for d in data:
            d_copy = copy.deepcopy(d)
            new_d = {}
            new_d['element_type'] = d_copy['element_type']
            new_d['element_subtype'] = d_copy['element_subtype']
            new_d['element_value'] = d_copy['element_value']

            if new_d["element_type"] == "ADDRESS":
                new_d["link"] = { "rel": "self", "href": "/api/addresses/" + new_d['element_value']}

            result['elements'].append(new_d)

        return result

    @classmethod
    def get_by_userid(cls, userid):

        d = cls.retrieve(template={"userid": userid})
        if d is not None and len(d) > 0:
            result =  cls._process_result(d)
        else:
            result = None

        return result

    @classmethod
    def get_by_profileid(cls, profileid):

        d = cls.retrieve(template={"profileid": profileid})
        if d is not None and len(d) > 0:
            result = cls._process_result(d)
        else:
            result = None

        return result

    @classmethod
    def create_profile_element(cls, p_element, commit=True, conn=None, cur=None):
        res = cls.insert(p_element, conn=conn, cursor=cur, commit=commit)
        return res

    @classmethod
    def create_profile(cls, profile_info, commit=False):

        result = None

        try:

            for el in profile_info['entries']:

                el['userid'] = profile_info['userid']
                el['profileid'] = profile_info['profileid']
                #res = cls.create_profile_element(el, commit=False, conn=conn, cur=cur)
                
                sql, args = data_adaptor.create_insert(table_name="profile", row=el)
                res, data = data_adaptor.run_q(sql, args) 
                if res != 1:
                    result = None
                else:
                    result = profile_info
            
        except pymysql.err.IntegrityError as ie:
            if ie.args[0] == 1062:
                raise (DataException(DataException.duplicate_key))
            else:
                raise DataException()
        except Exception as e:
            raise DataException()

        return result


    @classmethod
    def update_profile(cls, profileid, data):
        result = None
                 
        try:
            sql, args = data_adaptor.create_update(table_name="baseball.profile",\
                                                    new_values=data, \
                                                    template={"profileid":profileid})

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
    def delete_profile(cls, profileid):
        sql = "delete from baseball.profile where profileid=%s"
        res, data = data_adaptor.run_q(sql=sql, args=(profileid), fetch=True)
        if data is not None and len(data) > 0:
            result =  data[0]
        else:
            result = None
                                                                          
        return result

    @classmethod
    def retrieve(cls, template=None):
        if not template:
            return None 

        key = list(template.keys())[0]
        tid = template.get(key)

        sql = "select * from baseball.profile where " + key + "=\"" + tid  + "\""

        res, data = data_adaptor.run_q(sql=sql, args=(), fetch=True)
        if data is not None and len(data) > 0:
            result =  data
        else:
            result = None
                
        return result  
