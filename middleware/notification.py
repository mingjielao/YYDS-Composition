import requests
import json
import boto3

notification_paths = [
    "/api/events",
]


def format_message(text_message, event_type, resource_info):
    a_message = {
        "text": "*" + text_message + "*",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*State Change Event:*"
                }
            }
        ]
    }

    for k, v in resource_info.items():
        a_message["blocks"].append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": k + ":\t\t" + str(v)
                }
            }
        )

    return a_message


class NotificationMiddlewareHandler:
    sns_client = None

    def __init__(self):
        pass

    @classmethod
    def get_sns_client(cls):

        if NotificationMiddlewareHandler.sns_client is None:
            NotificationMiddlewareHandler.sns_client = sns = boto3.client("sns",
                                                                          region_name="us-east-2")
        return NotificationMiddlewareHandler.sns_client

    @classmethod
    def get_sns_topics(cls):
        s_client = NotificationMiddlewareHandler.get_sns_client()
        result = response = s_client.list_topics()
        topics = result["Topics"]
        return topics

    @classmethod
    def send_sns_message(cls, sns_topic, message):
        import json

        s_client = NotificationMiddlewareHandler.get_sns_client()
        response = s_client.publish(
            TopicArn=sns_topic,
            Message=json.dumps({'default': json.dumps(message)}),
            MessageStructure='json'
        )
        print("Publish response = ", json.dumps(response, indent=2))

    @staticmethod
    def notify(request, sns_topic):
        print(request.path)
        for path in notification_paths:
            if request.path.startswith(path):

                notification = {}

                try:
                    request_data = request.get_json()
                except Exception as e:
                    request_data = None

                path = request.path

                if request.method == 'POST':
                    notification["change"] = "CREATED"
                    notification['new_state'] = request_data
                    notification['params'] = path
                elif request.method == 'PUT':
                    notification["change"] = "UPDATE"
                    notification['new_state'] = request_data
                    notification["params"] = path
                elif request.method == "DELETE":
                    notification["change"] = "DELETED"
                    notification["params"] = path
                else:
                    notification = None
                # print(notification)
                NotificationMiddlewareHandler.send_sns_message(sns_topic, notification)
