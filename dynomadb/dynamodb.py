import boto3
from boto3.dynamodb.conditions import Key, Attr
import json
from datetime import datetime
import time
import uuid

# There is some weird stuff in DynamoDB JSON responses. These utils work better.
# I am not using  in this example.
# from dynamodb_json import json_util as jsond

# There are a couple of types of client.
# I create both because I like operations from both of them.
#
# I comment out the key information because I am getting this from
# my ~/.aws/credentials files. Normally this comes from a secrets vault
# or the environment.
#
dynamodb = boto3.resource('dynamodb',
                          aws_access_key_id="AKIA3G2MEQCFDAHOJZUX",
                          aws_secret_access_key="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",
                          region_name='us-east-2')

other_client = boto3.client("dynamodb",region_name='us-east-2')


def get_item(table_name, key_value):
    table = dynamodb.Table(table_name)

    response = table.get_item(
        Key=key_value
    )

    response = response.get('Item', None)
    return response



def put_item(table_name, item):

    table = dynamodb.Table(table_name)
    res = table.put_item(Item=item)
    return res


def add_relation(table_name, attribute_name1, attribute_name2, attribute_value1, attribute_value2):
    '''dt = time.time()
    dts = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(dt))'''

    item = {
        "relation_id": str(uuid.uuid4()),
        "version_id": str(uuid.uuid4()),
        attribute_name1: attribute_value1,
        attribute_name2: attribute_value2
    }

    res = put_item(table_name, item=item)

    return res


'''
    table_name = "User-Event"
    attribute_name = "user_id"
    attribute_value = "24"
    res = db.find_by_attribute(table_name, attribute_name, attribute_value)
    print("t2 -- res = ", json.dumps(res, indent=3))
    
    output:
    t2 -- res =  [
   {
      "event_id": "3",
      "user_id": "24",
      "version_id": "b8eb15c3-e4d0-4206-8518-0273bdf50cb5",
      "relation_id": "a27b2819-25aa-4f89-8a65-4951cf3d1aac"
   },
   {
      "event_id": "4",
      "user_id": "24",
      "version_id": "e044b512-5ffe-46b9-a4a4-2aada7198df0",
      "relation_id": "acb1d137-6cf1-4f54-965c-1f11e8105916"
   }
]
'''
def find_by_attribute(table_name, attribute_name, attribute_value):
    table = dynamodb.Table(table_name)

    expressionAttributes = dict()
    expressionAttributes[":S"] = attribute_value
    filterExpression = "contains(" + attribute_name + ", :S)"

    result = table.scan(FilterExpression=filterExpression,
                        ExpressionAttributeValues=expressionAttributes)
    json.dumps(result, indent=3)
    return result["Items"]


def write_relation_if_not_changed(tabale_name, new_relation, old_relation):

    new_version_id = str(uuid.uuid4())
    new_relation["version_id"] = new_version_id

    old_version_id = old_relation["version_id"]

    table = dynamodb.Table(tabale_name)

    res = table.put_item(
        Item=new_relation,
        ConditionExpression="version_id=:old_version_id",
        ExpressionAttributeValues={":old_version_id": old_version_id}
    )

    return res
