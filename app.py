import os
from flask import Flask, Response, request, redirect, url_for, session
from flask_cors import CORS
import json
import logging

from utils.rest_utils import RESTContext
from middleware.service_factory import ServiceFactory
from flask_dance.contrib.google import make_google_blueprint, google
import middleware.security as security

from middleware.notification import NotificationMiddlewareHandler

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
CORS(app)

client_id = "760166083721-g03if15thd5a5i1ceeuqkr60m729o8pl.apps.googleusercontent.com"
client_secret = "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"
app.secret_key = "some secret"

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

blueprint = make_google_blueprint(
    client_id=client_id,
    client_secret=client_secret,
    reprompt_consent=True,
    scope=["profile", "email"],
)
app.register_blueprint(blueprint, url_prefix="/login")
g_bp = app.blueprints.get("google")


@app.before_request
def before_request_func():
    try:
        result_ok = security.check_security(request, google, g_bp)
    except Exception as e:  # or maybe any OAuth2Error
        return redirect(url_for("google.login"))
    print("before request...")
    if not result_ok:
        return redirect(url_for("google.login"))


@app.after_request
def after_request_func(response):
    print("after_request is running!")
    NotificationMiddlewareHandler.notify(request, "arn:aws:sns:us-east-2:770569437322:notification")
    return response


@app.route('/')
def hello_world():
    return '<u>Hello World!</u>'


@app.route('/api/<resource_collection>', methods=["GET", "POST"])
def do_resource_collection(resource_collection):
    request_inputs = RESTContext(request, resource_collection)
    service = ServiceFactory()
    svc = service.get_service(resource_collection)

    if svc is None:
        rsp = Response(json.dumps("Resource not found", default=str), status=404, content_type="application/json")
    elif request_inputs.method == "GET":
        res = svc.get_by_template(request_inputs.args,
                                  field_list=request_inputs.fields,
                                  limit=request_inputs.limit,
                                  offset=request_inputs.offset)
        # res = request_inputs.add_pagination(res)
        rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
    elif request_inputs.method == "POST":
        res = svc.create(request.get_json())
        if res == -1:
            rsp = Response(json.dumps("Bad data", default=str), status=400, content_type="application/json")
        else:
            rsp = Response(json.dumps(res, default=str), status=201, content_type="application/json")

    return rsp


@app.route('/api/<resource_collection>/<resource_id>', methods=["GET", "PUT", "DELETE"])
def specific_resource(resource_collection, resource_id):
    request_inputs = RESTContext(request, resource_collection)
    service = ServiceFactory()
    svc = service.get_service(resource_collection)

    if svc is None:
        rsp = Response(json.dumps("Resource not found", default=str), status=404, content_type="application/json")
    elif request_inputs.method == "GET":
        res = svc.get_by_resource_id(resource_id, field_list=request_inputs.fields)
        if res == ():
            rsp = Response(json.dumps("Id not found", default=str), status=404, content_type="application/json")
        else:
            rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
    elif request_inputs.method == "PUT":
        res = svc.put_by_resource_id(resource_id, request.get_json())
        rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
    elif request_inputs.method == "DELETE":
        res = svc.delete_by_resource_id(resource_id)
        rsp = Response(json.dumps(res, default=str), status=204, content_type="application/json")
    return rsp


@app.route('/api/event/<resource_id>/<linked_resource>', methods=["GET"])
def linked_resource(resource_id, linked_resource):
    request_inputs = RESTContext(request, "event")
    service = ServiceFactory()
    svc = service.get_service("event")
    linked_svc = service.get_service(linked_resource)

    if linked_svc is None:
        rsp = Response(json.dumps("Linked resource not found", default=str), status=404,
                       content_type="application/json")
    elif linked_resource == "eventvenue" or linked_resource == "eventtype" or linked_resource == "eventorganizer":
        field_name = linked_resource[5:] + "_id"
        res = linked_svc.get_by_resource_id(
            str(svc.get_by_resource_id(resource_id, field_list=[field_name])[0][field_name]),
            field_list=request_inputs.fields)
        rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
    return rsp


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
