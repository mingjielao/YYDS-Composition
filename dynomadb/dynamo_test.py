import json
import dynamodb as db
import copy
import uuid


def t1():

    res = db.get_item("User-Event",
                      {
                          "user_id": "1"
                      })
    print("Result = \n", json.dumps(res, indent=4, default=str))

#find_by_attribute(table_name, attribute_name, attribute_value):
def t2():
    table_name = "User-Event"
    attribute_name = "event_id"
    attribute_value = "5"
    res = db.find_by_attribute(table_name, attribute_name, attribute_value)
    print("t2 -- res = ", json.dumps(res, indent=3))

def t3():
    table_name = "User-Event"
    attribute1_name = "user_id"
    attribute2_name = "event_id"
    attribute1_value = "24"
    attribute2_value = "4"
    res = db.add_relation(table_name, attribute1_name,attribute2_name, attribute1_value, attribute2_value)
    print("t3 -- res = ", json.dumps(res, indent=3))


def t6():

    comment_id = "a27b2819-25aa-4f89-8a65-4951cf3d1aac"
    original_relation = db.get_item("User-Event",{
        "relation_id": "a27b2819-25aa-4f89-8a65-4951cf3d1aac"
    })
    original_version_id = original_relation["version_id"]

    new_relation = copy.deepcopy(original_relation)

    try:
        res = db.write_relation_if_not_changed("User-Event", original_relation, new_relation)
        print("First write returned: ", res)
    except Exception as e:
        print("First write exception = ", str(e))

    try:
        res = db.write_relation_if_not_changed("User-Event", original_relation, new_relation)
        print("Second write returned: ", res)
    except Exception as e:
        print("Second write exception = ", str(e))


#t1()
t2()
#t3()
#t4()
#t5()
#t6()