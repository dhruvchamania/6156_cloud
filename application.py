
# Import functions and objects the microservice needs.
# - Flask is the top-level application. You implement the application by adding methods to it.
# - Response enables creating well-formed HTTP/REST responses.
# - requests enables accessing the elements of an incoming HTTP/REST request.
#
from flask import Flask, Response, request
from flask_cors import CORS
from DataAccess.DataObject import UsersRDB as UsersRDB
from datetime import datetime
import json
import uuid
from CustomerInfo.Users import UsersService as UserService
from RegisterLogin.RegisterLogin import RegisterLoginSvc as RegisterLoginSvc
#from RegisterLogin.AddressService import AddressService as AddressService
from Context.Context import Context
from functools import wraps
#from Middleware import notification
import Middleware.security as security_middleware
import Middleware.notification as notification_middleware
from hashlib import  sha3_256

#from botocore.vendored import requests
import requests as req

# Setup and use the simple, common Python logging framework. Send log messages to the console.
# The application should get the log level out of the context. We will change later.
#

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("\nDecorator was called!!!!. Request = ", request)
        return f(*args, **kwargs)
    return decorated_function

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

###################################################################################################################
#
# AWS put most of this in the default application template.
#
# AWS puts this function in the default started application
# print a nice greeting.
def say_hello(username = "World"):
    return '<p>Hello %s!</p>\n' % username

# AWS put this here.
# some bits of text for the page.
header_text = '''
    <html>\n<head> <title>EB Flask Test</title> </head>\n<body>'''
instructions = '''
    <p><em>Hint</em>: This is a RESTful web service! Append a username
    to the URL (for example: <code>/Thelonious</code>) to say hello to
    someone specific.</p>\n'''
home_link = '<p><a href="/">Back</a></p>\n'
footer_text = '</body>\n</html>'

# EB looks for an 'application' callable by default.
# This is the top-level application that receives and routes requests.
from Middleware.middleware import SimpleMiddleWare as SimpleM
from Context.Context import Context
from Services.CustomerProfile.Profile import ProfileService as ProfileService
_profile_service = None

application = Flask(__name__)

CORS(application)

# Middleware
application.wsgi_app = SimpleM(application.wsgi_app)


@application.before_request
def before_decorator():
    print(".... In before decorator ...")
    # pull auth header from request
    # check with security middleware that it's the expected user
    if 'Authorization' in request.headers:
        print('got request with auth header')
        uri = request.path
        method = request.method
        auth_token = request.headers.get('Authorization')
        if not security_middleware.authorize(uri, method, auth_token):
            print("authentication failed")
            rsp_data = None
            rsp_status = 403
            rsp_txt = "NOT AUTHORIZED"
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")
            return full_rsp



@application.after_request
def after_decorator(rsp):
    print("... In after decorator ...")
    return rsp

# add a rule for the index page. (Put here by AWS in the sample)
application.add_url_rule('/', 'index', (lambda: header_text +
    say_hello() + instructions + footer_text))

# add a rule when the page is accessed with a name appended to the site
# URL. Put here by AWS in the sample
application.add_url_rule('/<username>', 'hello', (lambda username:
    header_text + say_hello(username) + home_link + footer_text))

##################################################################################################################
# The stuff I added begins here.

_default_context = None
_user_service = None
_registration_service = None

def _get_default_context():

    global _default_context

    if _default_context is None:
        _default_context = Context.get_default_context()

    return _default_context

def _get_profile_service():
    global _profile_service

    if _profile_service is None:
        _profile_service = ProfileService()

    return _profile_service

def _get_user_service():
    global _user_service

    if _user_service is None:
        _user_service = UserService(_get_default_context())

    return _user_service

def _get_registration_service():
    global _registration_service

    if _registration_service is None:
        _registration_service = RegisterLoginSvc()

    return _registration_service


def init():

    global _default_context, _user_service, _profile_service

    _default_context = Context.get_default_context()
    _user_service = UserService(_default_context)
    _registration_service = RegisterLoginSvc()
    _profile_service = ProfileService(_default_context)

    logger.debug("_user_service = " + str(_user_service))
    logger.debug("_profile_service = " + str(_profile_service))


# 1. Extract the input information from the requests object.
# 2. Log the information
# 3. Return extracted information.
#
def log_and_extract_input(method, path_params=None):

    path = request.path
    args = dict(request.args)
    data = None
    headers = dict(request.headers)
    method = request.method

    try:
        if request.data is not None:
            data = request.json
        else:
            data = None
    except Exception as e:
        # This would fail the request in a more real solution.
        data = "You sent something but I could not get JSON out of it."

    log_message = str(datetime.now()) + ": Method " + method

    inputs =  {
        "path": path,
        "method": method,
        "path_params": path_params,
        "query_params": args,
        "headers": headers,
        "body": data
        }

    log_message += " received: \n" + json.dumps(inputs, indent=2)
    logger.debug(log_message)

    return inputs

def log_response(method, status, data, txt):

    msg = {
        "method": method,
        "status": status,
        "txt": txt,
        "data": data
    }

    logger.debug(str(datetime.now()) + ": \n" + json.dumps(msg, indent=2))


# This function performs a basic health check. We will flesh this out.
@application.route("/health", methods=["GET"])
def health_check():

    rsp_data = { "status": "healthy", "time": str(datetime.now()) }
    rsp_str = json.dumps(rsp_data)
    rsp = Response(rsp_str, status=200, content_type="application/json")
    return rsp


@application.route("/demo/<parameter>", methods=["GET", "POST"])
def demo(parameter):

    inputs = log_and_extract_input(demo, { "parameter": parameter })

    msg = {
        "/demo received the following inputs" : inputs
    }

    rsp = Response(json.dumps(msg), status=200, content_type="application/json")
    return rsp


@application.route("/api/profile", methods=["POST", "GET"])
def handle_profiles():
    inputs = log_and_extract_input(demo, {"parameters": None})
    rsp_data = None
    rsp_status = None
    rsp_txt = None

    try:

        r_svc = _get_profile_service()

        logger.error("/profile_service = " + str(r_svc))

        if inputs["method"] == "POST":
            rsp = r_svc.create_profile(inputs['body'])

            if rsp is not None:
                rsp_data = rsp
                rsp_status = 201
                rsp_txt = "CREATED"
                link = "?userid=" + rsp_data['userid']
            else:
                rsp_data = None
                rsp_status = 501
                rsp_txt = "INTERNAL ERROR"

        elif inputs["method"] == "GET":
            query = inputs['query_params']
            rsp = r_svc.get_by_userid(query['customerid'])

            if rsp is not None:
                rsp_data = rsp
                rsp_status = 201
                rsp_txt = "FOUND"
                link = "?userid=" + rsp_data['userid']
            else:
                rsp_data = None
                rsp_status = 502
                rsp_txt = "NOT FOUND"

        else:
            rsp_data = None
            rsp_status = 501
            rsp_txt = "NOT IMPLEMENTED"

        if rsp_data is not None:
            # TODO Generalize generating links
            headers = {"Location": "/api/users" + link}
            # headers["Authorization"] =  auth
            rsp_data['links'] = {"rel": "user", "href": headers['Location']}

            full_rsp = Response(json.dumps(rsp_data), headers=headers, \
                                status=rsp_status, content_type="text/plain")
        else:
            full_rsp = Response(rsp_data, status=rsp_status, content_type="text/plain")

    except Exception as e:
        log_msg = "/api/profile: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/api/registration", rsp_status, rsp_data, rsp_txt)

    return full_rsp

@application.route('/api/<resource>/<primary_key>', methods=["GET"])
def handle_resource_prim(resource,primary_key):
    global _user_service

    inputs = log_and_extract_input(demo, {"parameters": primary_key})
    rsp_data = None
    rsp_status = None
    rsp_txt = None

    try:

        user_service = _get_user_service()

        logger.error("/userid: _user_service = " + str(user_service))

        if inputs["method"] == "GET":

            account = user_service.get_by_userid(primary_key)
            if account["status"] == "DELETED":
                rsp = "User is already deleted"
            else:
                rsp = account

            if rsp is not None:
                rsp_data = rsp
                rsp_status = 200
                rsp_txt = "OK"
            else:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "NOT FOUND"

        if rsp_data is not None:
            full_rsp = Response(json.dumps(rsp_data), status=rsp_status, content_type="application/json")
        else:
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    except Exception as e:
        log_msg = "/userid: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/userid", rsp_status, rsp_data, rsp_txt)

    return full_rsp

@application.route('/api/<resource>', methods=["GET"])
def handle_resource(resource):
    global _user_service

    field_list = request.args.get('fields', None)
    field_list = field_list.split(',')
    inputs = log_and_extract_input(demo, {"parameters": resource})
    rsp_data = None
    rsp_status = None
    rsp_txt = None
    tmp = None
    for k, v in request.args.items():
        if (not k == 'fields') and (not k == 'limit') and (not k == 'offset') and (not k == 'order_by'):
            if tmp is None:
                tmp = {}
            tmp[k] = v

    try:

        user_service = _get_user_service()

        logger.error("/Query: _user_service = " + str(user_service))

        if inputs["method"] == "GET":

            rsp = user_service.get_by_query(tmp,field_list)
            if rsp is not None:
                rsp_data = rsp
                rsp_status = 200
                rsp_txt = "OK"
            else:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "NOT FOUND"

        if rsp_data is not None:
            full_rsp = Response(json.dumps(rsp_data), status=rsp_status, content_type="application/json")
        else:
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    except Exception as e:
        log_msg = "/Query: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/Query", rsp_status, rsp_data, rsp_txt)

    return full_rsp


@application.route("/api/profile/<profileid>", methods=["GET", "PUT", "DELETE"])
def handle_profile_profileid(profileid):
    global _profile_service

    inputs = log_and_extract_input(demo, {"parameters": profileid})

    rsp_data = None
    rsp_status = None
    rsp_txt = None

    try:
        profile_service = _get_profile_service()

        logger.info("/profileid: _profile_service = " + str(_profile_service))

        if inputs["method"] == "GET":
            rsp = profile_service.get_by_profileid(profileid)

            if rsp is not None:
                rsp_data = rsp
                rsp_status = 200
                rsp_txt = "OK"
            else:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "NOT FOUND"

        elif inputs["method"] == "PUT":
            body = inputs['body']
            rsp = profile_service.update_by_profileid(profileid, body)

            if rsp is not None:
                rsp_data = rsp
                rsp_status = 200
                rsp_txt = "OK"
            else:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "NOT FOUND"

        elif inputs["method"] == "DELETE":
            rsp = profile_service.delete_by_profileid(profileid)

            if rsp is not None:
                rsp_data = rsp
                rsp_status = 200
                rsp_txt = "OK"
            else:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "NOT FOUND"

        else:
            rsp_data = None
            rsp_status = 501
            rsp_txt = "NOT IMPLEMENTED"

        if rsp_data is not None:
            headers = {"Location": "/api/users" + link}
            # headers["Authorization"] =  auth
            rsp_data['links'] = {"rel": "user", "href": headers['Location']}

            full_rsp = Response(json.dumps(rsp_data, default=str),
                                status=rsp_status,
                                headers=headers,
                                content_type="application/json")
        else:
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    except Exception as e:
        log_msg = "/userid: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/userid", rsp_status, rsp_data, rsp_txt)

    return full_rsp


@application.route("/api/user/", methods = ["POST"])
def user():

   global _user_service


   resource_name = request.get_json()
   resource_name['id'] = str(uuid.uuid4())

   inputs = log_and_extract_input(demo, resource_name)
   #rsp_data = None
   rsp_data = None

   try:

       user_service = _get_user_service()

       if request.method == "POST":

            rsp = user_service.create_user(resource_name)

            if rsp is not None:
                rsp_data = rsp
                rsp_status = 200
                rsp_txt = "User Created"
            else:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "NOT FOUND"
       elif request.method == "GET":
           rsp_data = user_service.get_by_email(resource_name["email"])



   except Exception as e:
       log_msg = "/email: Exception = " + str(e)
       logger.error(log_msg)
       rsp_status = 500
       rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
       full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

   #print(rsp)
   #return rsp
   return rsp_data

@application.route("/api/user/<email>", methods=["PUT", "DELETE", "GET"])
def user_email(email):

    global _user_service

    inputs = log_and_extract_input(demo, { "parameters": email })
    rsp_data = None
    rsp_status = None
    rsp_txt = None

    try:

        user_service = _get_user_service()

        logger.error("/email: _user_service = " + str(user_service))

        if inputs["method"] == "GET":

            account = user_service.get_by_email(email)
            if account["status"] == "DELETED":
                rsp = "User is already deleted"
            else:
                rsp = account

            if rsp is not None:
                rsp_data = rsp
                rsp_status = 200
                rsp_txt = "OK"
            else:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "NOT FOUND"

        elif request.method == "DELETE":

            account = user_service.get_by_email(email)
            if account["status"] == "DELETED":
                rsp = "User is already deleted"
            else:
                rsp = user_service.delete_user(user_info=account)

            if rsp is not None:
                rsp_data = rsp
                rsp_status = 404
                rsp_txt = "OK"
            else:
                rsp_data = "Succesfully deleted"
                rsp_status = 200
                rsp_txt = "Data Sucessfully Deleted"

        elif inputs["method"] == "PUT":
            rsp_data = None
            # rsp_status = 501
            # rsp_txt = "NOT IMPLEMENTED"
            resource_name = request.get_json()
            account = user_service.get_by_email(email)
            if account["status"] == "DELETED":
                rsp = "User is already deleted"
            else:
                rsp = user_service.update_user(email, data=json.loads(request.get_data()))
            if rsp is not None:
                rsp_data = rsp
                rsp_status = 404
                rsp_txt = "OK"
            else:
                rsp_data = "Succesfully updated"
                rsp_status = 200
                rsp_txt = "Data Sucessfully Updated"



        if rsp_data is not None:
            full_rsp = Response(json.dumps(rsp_data), status=rsp_status, content_type="application/json")
        else:
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    except Exception as e:
        log_msg = "/email: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/email", rsp_status, rsp_data, rsp_txt)

    return full_rsp

@application.route("/api/registration", methods=["POST"])
def registration():

    inputs = log_and_extract_input(registration, {"parameters": None})
    rsp_data = None
    rsp_status = None
    rsp_txt = None

    try:

        r_svc = _get_registration_service()

        logger.error("/api/registration: _r_svc = " + str(r_svc))

        if inputs["method"] == "POST":

            rsp = r_svc.register(inputs['body'])

            if rsp is not None:
                rsp_data = rsp
                rsp_status = 201
                rsp_txt = "CREATED"
                link = rsp_data[0]
                auth = rsp_data[1]
            else:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "NOT FOUND"
        else:
            rsp_data = None
            rsp_status = 501
            rsp_txt = "NOT IMPLEMENTED"

        if rsp_data is not None:
            # TODO Generalize generating links
            headers = {"Location": "/api/users/" + link}
            headers["Authorization"] =  auth
            full_rsp = Response(rsp_txt, headers=headers,
                                status=rsp_status, content_type="text/plain")
        else:
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    except Exception as e:
        log_msg = "/api/registration: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/api/registration", rsp_status, rsp_data, rsp_txt)

    return full_rsp


@application.route("/api/login", methods=["POST"])
def login():
    inputs = log_and_extract_input(login, {"parameters": None})
    rsp_data = None
    rsp_status = None
    rsp_txt = None

    try:

        r_svc = _get_registration_service()

        logger.error("/api/login: _r_svc = " + str(r_svc))

        if inputs["method"] == "POST":

            rsp = r_svc.login(inputs['body'])

            if rsp is not False:
                rsp_data = "OK"
                rsp_status = 201
                rsp_txt = "CREATED"
            else:
                rsp_data = None
                rsp_status = 403
                rsp_txt = "NOT AUTHORIZED"
        else:
            rsp_data = None
            rsp_status = 501
            rsp_txt = "NOT IMPLEMENTED"

        if rsp_data is not None:
            # TODO Generalize generating links
            headers = {"Authorization": rsp}
            full_rsp = Response(json.dumps(rsp_data, default=str), headers=headers,
                                status=rsp_status, content_type="application/json")
        else:
            full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    except Exception as e:
        log_msg = "/api/registration: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/api/registration", rsp_status, rsp_data, rsp_txt)

    return full_rsp


@application.route("/api/test_middleware/<parameter>", methods=["GET", "PUT", "DELETE", "POST"])
def test_middleware(parameter):

    security_middleware.authorize(request.url, request.method,
                                  request.headers.get("Authorization", None))
    logger.debug("/api/user/<email>" + json.dumps(request, default=str))

    # Other middleware goes here ...


    # Now do the application functions.


    # And now do the functions for post processing the request.
    logger.debug("/api/user/<email>" + json.dumps(request, default=str))
    if request.method in ('POST', 'PUT', 'DELETE'):
        notification_middleware.publish_change_event(request.url, request.json)

    # More stuff goes here.

    return "something"

@application.route("/api/addresses", methods=["POST","PUT"])
def create_address():
    address_body = request.get_json()

    # in_args, fields, body, limit, offset = parse_and_print_args()
    # address_info = body
    print("POST body =", address_body)
    inputs = log_and_extract_input(demo, {"parameters": address_body['body']})
    full_rsp = None
    rsp_data = None
    rsp_status = None
    rsp_txt = None
    base_url = request.url_root
    try:


        rsp = None

        if inputs["method"] == "POST":
            url = "https://8qhflxznug.execute-api.us-east-1.amazonaws.com/alpha/api-address"
            headers = {
                'Content-type': 'application/json'

            }
            lambda_response = req.post(url, json=address_body, headers= headers) #address_service.address(address_body['body'])
            lamb = lambda_response.json()
            if lambda_response is not None:

                if 'body' in lamb.keys():

                    url = "https://8qhflxznug.execute-api.us-east-1.amazonaws.com/alpha/api-address"#base_url + 'api/profile'
                    profile_data = {
                        'address_id': lamb['body'][1:-1],
                        'userid': address_body['userid']
                    }
                    print("before post")
                    print(profile_data)
                    profile_service = _get_profile_service()
                    rsp = profile_service.update_by_profileid('dhruv_profile3', profile_data)
                    print("after post")
                    rsp_data = lamb['body']
                    rsp_status = 200
                    # rsp_txt = "OK"
                    rsp_txt = "Address created successfully"
                else:
                    rsp_data = None
                    rsp_status = 404
                    rsp_txt = "Address is invalid "
            else:
                rsp_data = None
                rsp_status = 404
                rsp_txt = "Error in state machine"

    except Exception as e:
        log_msg = "address create: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "Exception in address creation"

    full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/create address", rsp_status, rsp_data, rsp_txt)

    return full_rsp


logger.debug("__name__ = " + str(__name__))
# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.


    logger.debug("Starting Project EB at time: " + str(datetime.now()))
    init()

    application.debug = True
    # application.run()