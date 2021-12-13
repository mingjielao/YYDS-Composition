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

@app.route('/recommendedEvents/<user_id>', methods=["GET"])
def recommendedEvents(user_id):
    # All event ids that user joined
    joinedEventIds = set(ast.literal_eval(requests.get(USER_ENDPOINT + '/getEvents/' + user_id).text))

    # All group ids that user joined
    joinedGroupIds = ast.literal_eval(requests.get(USER_ENDPOINT + '/getGroups/' + user_id).text)

    recommendedEventList = []
    for joinedGroupId in joinedGroupIds:
        # All event ids inside the group that user joined
        eventIdsInJoinedGroup = ast.literal_eval(requests.get(GROUP_ENDPOINT + '/getEvents/' + joinedGroupId).text)
        for eventIdInJoinedGroup in eventIdsInJoinedGroup:
            # if this event id inside (the group that user joined) is not joined by user, append the event info
            if eventIdInJoinedGroup not in joinedEventIds:
                recommendedEventList.append(requests.get(EVENT_ENDPOINT + '/event/' + eventIdInJoinedGroup).text)
    return Response(json.dumps(recommendedEventList, default=list), status=200, content_type="application/json")

@app.route('/getMyEvents', methods=["GET"])
def registeredEvents():
    eventIds = ast.literal_eval(requests.get(USER_ENDPOINT + '/getEvents/1').text)

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
    res = requests.delete(USER_ENDPOINT + '/removeEvent/' + user + '/' + event).text
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




async def userAddGroup(user, group):
    res = requests.post(USER_ENDPOINT + '/addGroup/' + user + '/' + group).text
    return res

async def groupAddUser(group, user):
    res = requests.post(GROUP_ENDPOINT + '/addUser/' + group + '/' + user).text
    return res

async def addUserGroupRelation(user_id, group_id):
    await asyncio.gather(userAddGroup(user_id, group_id), groupAddUser(group_id, user_id))

async def userRemoveGroup(user, group):
    res = requests.delete(USER_ENDPOINT + '/removeGroup/' + user + '/' + group).text
    return res

async def groupRemoveUser(group, user):
    res = requests.delete(GROUP_ENDPOINT + '/removeUser/' + group + '/' + user).text
    return res

async def removeUserGroupRelation(user_id, group_id):
    await asyncio.gather(userRemoveGroup(user_id, group_id), groupRemoveUser(group_id, user_id))

@app.route('/addUserGroup/<user_id>/<group_id>', methods=["POST"])
def addUserGroup(user_id, group_id):
    asyncio.run(addUserGroupRelation(user_id, group_id))
    return Response(json.dumps('Success', default=str), status=200, content_type="application/json")

@app.route('/removeUserGroup/<user_id>/<group_id>', methods=["DELETE"])
def removeUserGroup(user_id, group_id):
    asyncio.run(removeUserGroupRelation(user_id, group_id))
    return Response(json.dumps('Success', default=str), status=200, content_type="application/json")





async def eventAddGroup(event, group):
    res = requests.post(EVENT_ENDPOINT + '/addGroup/' + event + '/' + group).text
    return res


async def groupAddEvent(group, event):
    res = requests.post(GROUP_ENDPOINT + '/addEvent/' + group + '/' + event).text
    return res


async def addEventGroupRelation(event_id, group_id):
    await asyncio.gather(eventAddGroup(event_id, group_id), groupAddEvent(group_id, event_id))


async def eventRemoveGroup(event, group):
    res = requests.delete(EVENT_ENDPOINT + '/removeGroup/' + event + '/' + group).text
    return res


async def groupRemoveEvent(group, event):
    res = requests.delete(GROUP_ENDPOINT + '/removeEvent/' + group + '/' + event).text
    return res


async def removeEventGroupRelation(event_id, group_id):
    await asyncio.gather(eventRemoveGroup(event_id, group_id), groupRemoveEvent(group_id, event_id))


@app.route('/addEventGroup/<event_id>/<group_id>', methods=["POST"])
def addEventGroup(event_id, group_id):
    asyncio.run(addEventGroupRelation(event_id, group_id))
    return Response(json.dumps('Success', default=str), status=200, content_type="application/json")


@app.route('/removeEventGroup/<event_id>/<group_id>', methods=["DELETE"])
def removeEventGroup(event_id, group_id):
    asyncio.run(removeEventGroupRelation(event_id, group_id))
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
