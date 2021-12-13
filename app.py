import os
from flask import Flask, Response, request, redirect, url_for, session
from flask_cors import CORS
import json
import logging
import requests
import asyncio
import ast
import boto3

from utils.rest_utils import RESTContext
from middleware.service_factory import ServiceFactory
from flask_dance.contrib.google import make_google_blueprint, google
import middleware.security as security

from compo_tests import compo_test

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


# @app.before_request
# def before_request_func():
#     try:
#         result_ok = security.check_security(request, google, g_bp)
#     except Exception as e:  # or maybe any OAuth2Error
#         return redirect(url_for("google.login"))
#     print("before request...")
#     if not result_ok:
#         return redirect(url_for("google.login"))


@app.after_request
def after_request_func(response):
    print("after_request is running!")
    NotificationMiddlewareHandler.notify(request, "arn:aws:sns:us-east-2:770569437322:notification")
    return response


@app.route('/')
def hello_world():
    compo_test.test_async()
    return '<u>Hello World!</u>'


API_ENDPOINT = 'https://m6p93ab8g4.execute-api.us-east-2.amazonaws.com/prod'
USER_ENDPOINT = 'https://m6p93ab8g4.execute-api.us-east-2.amazonaws.com/prod/user'
EVENT_ENDPOINT = 'https://m6p93ab8g4.execute-api.us-east-2.amazonaws.com/prod/event'
GROUP_ENDPOINT = 'https://m6p93ab8g4.execute-api.us-east-2.amazonaws.com/prod/group'


@app.route('/getMyEvents', methods=["GET"])
def getMyEvents():
    eventIds = ast.literal_eval(requests.get(USER_ENDPOINT + '/getEvent/1').text)

    eventList = []
    for eventId in eventIds:
        a = requests.get(EVENT_ENDPOINT + '/event/' + eventId)
        eventList.append(requests.get(EVENT_ENDPOINT + '/event/' + eventId).text)

    return Response(json.dumps(eventList, default=list), status=200, content_type="application/json")

async def userAddEvent(user, event):
    res = requests.post(USER_ENDPOINT + '/addEvent/' + user + '/' + event).text
    return res

async def eventAddUser(event, user):
    res = requests.post(EVENT_ENDPOINT + '/addUser/' + event + '/' + user).text
    return res

async def addUserEventRelation(user_id, event_id):
    await asyncio.gather(userAddEvent(user_id, event_id), eventAddUser(event_id, user_id))

async def userRemoveEvent(user, event):
    a = requests.delete(USER_ENDPOINT + '/removeEvent/' + user + '/' + event)
    res = a.json()
    return res

async def eventRemoveUser(event, user):
    res = requests.delete(EVENT_ENDPOINT + '/removeUser/' + event + '/' + user).text
    return res

async def removeUserEventRelation(user_id, event_id):
    await asyncio.gather(userRemoveEvent(user_id, event_id), eventRemoveUser(event_id, user_id))

@app.route('/addUserEvent/<user_id>/<event_id>', methods=["POST"])
def addUserEvent(user_id, event_id):
    asyncio.run(addUserEventRelation(user_id, event_id))
    return Response(json.dumps('Success', default=str), status=200, content_type="application/json")

@app.route('/removeUserEvent/<user_id>/<event_id>', methods=["DELETE"])
def removeUserEvent(user_id, event_id):
    asyncio.run(removeUserEventRelation(user_id, event_id))
    return Response(json.dumps('Success', default=str), status=200, content_type="application/json")

@app.route('/getEventDetails/<event_id>', methods=["GET"])
def getEventDetail(event_id):
    client = boto3.client('stepfunctions')
    response = client.start_sync_execution(
        stateMachineArn='arn:aws:states:us-east-2:770569437322:stateMachine:MyStateMachineSync',
        name='get-event-detail',
        input=json.dumps({"event_id":event_id})
    )
    res = json.loads(response['output'])['body']
    return Response(res, status=200, content_type="application/json")

@app.route('/createNewEvent', methods=["POST"])
def creatNewEvent():
    organizer_id = 1
    starttime = request.json['starttime']
    endtime = request.json['endtime']
    description = request.json['description']
    type_id = request.json['type_id']
    venue_json = request.json['venue']
		
    res = json.loads(requests.post(EVENT_ENDPOINT + '/eventvenue', json=venue_json).content)
    new_venue_id = res['location'].split('/')[3]

    new_event_json = {'organizer_id': organizer_id, 'type_id': type_id, 'venue_id': new_venue_id, 'starttime': starttime, 'endtime': endtime, 'description': description}
    result = requests.post(EVENT_ENDPOINT + '/event', json=new_event_json).text
    new_event_id=(json.loads(result)['location'].split('/'))[3]

    asyncio.run(addUserEventRelation(str(organizer_id), new_event_id))
    return result

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
