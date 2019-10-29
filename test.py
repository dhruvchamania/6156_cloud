from flask import Flask, Response, request

from datetime import datetime
import json
import uuid

from CustomerInfo.Users import UsersService as UserService
from Context.Context import Context

from abc import ABC, abstractmethod
from Context.Context import Context
from DataAccess.DataObject import UsersRDB as UsersRDB

# Setup and use the simple, common Python logging framework. Send log messages to the console.
# The application should get the log level out of the context. We will change later.
#
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

#Get Email
def t1():

    r = UsersRDB.get_by_email('dhruv.chamania@gmail.com')
    print("Result = \n", json.dumps(r, indent=2))

# Create User
def t2():

    usr = {
        "last_name":"Baggins",
        "first_name":"Frodo",
        "id":str(uuid.uuid4()),
        "email":"dhruv.chamania432@gmail.com",
        "status":"Pending",
        "password":"ok"
    }
    res = UsersRDB.create_user(user_info=usr)

# Delete the above created user by email

def t3():
    r = UsersRDB.delete_by_email('dhruv.chamania@gmail.com')
    print("Result = \n", json.dumps(r, indent=2))

#t1()
t2()
#t3()