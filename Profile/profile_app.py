
# Import functions and objects the microservice needs.
# - Flask is the top-level application. You implement the application by adding methods to it.
# - Response enables creating well-formed HTTP/REST responses.
# - requests enables accessing the elements of an incoming HTTP/REST request.
#
import json
# Setup and use the simple, common Python logging framework. Send log messages to the console.
# The application should get the log level out of the context. We will change later.
#
import logging
from datetime import datetime
from functools import wraps

from flask import Flask, Response
from flask import request

import Middleware.notification as notification_middleware
import Middleware.security as security_middleware
from Context.Context import Context
from Services.CustomerProfile.Profile import ProfileService as ProfileService

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

_application_name = 'baseball'

_default_context = None
_profile_service = None

Context.set_application_name(_default_context)


application = Flask(__name__)


@application.before_request
def before_decorator():
    print(".... In before decorator ...")


@application.after_request
def after_decorator(rsp):
    print("... In after decorator ...")
    return rsp

def _get_default_context():

    global _default_context

    if _default_context is None:
        _default_context = Context.get_default_context(application_name=_application_name)

    return _default_context


def _get_profile_service():
    global _profile_service

    if _profile_service is None:
        _profile_service = ProfileService()

    return _profile_service


def init():

    global _default_context, _profile_service

    _default_context = Context.get_default_context()
    _profile_service = ProfileService(_default_context)

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

    logger.debug(str(datetime.now()) + ": \n" + json.dumps(msg, indent=2, default=str))


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
            #headers["Authorization"] =  auth
            rsp_data['links'] = {"rel":"user", "href": headers['Location']} 

            full_rsp = Response(json.dumps(rsp_data), headers=headers, \
                                status=rsp_status, content_type="text/plain")
        else:
            full_rsp = Response(rsp_data, status=rsp_status, content_type="text/plain")

    except Exception as e:
        log_msg = "/api/registration: Exception = " + str(e)
        logger.error(log_msg)
        rsp_status = 500
        rsp_txt = "INTERNAL SERVER ERROR. Please take COMSE6156 -- Cloud Native Applications."
        full_rsp = Response(rsp_txt, status=rsp_status, content_type="text/plain")

    log_response("/api/registration", rsp_status, rsp_data, rsp_txt)

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
            #headers["Authorization"] =  auth
            rsp_data['links'] = {"rel":"user", "href": headers['Location']}

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




def do_something_before():
    print("\n")
    print("***************** Do something before got ... **************", request)
    print("\n")


def do_something_after(rsp):
    print("\n")
    print("***************** Do something AFTER got ... **************", request)
    print("\n")
    return rsp



logger.debug("__name__ = " + str(__name__))


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.


    logger.debug("Starting Project EB at time: " + str(datetime.now()))
    init()

    application.debug = True
    application.before_request(do_something_before)
    application.after_request(do_something_after)
    application.run(port=5033)
