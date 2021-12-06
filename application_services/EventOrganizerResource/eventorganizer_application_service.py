import requests
from framework.base_application_resource import BaseApplicationResource
import json
class EventOrganizerResource(BaseApplicationResource):

    def __init__(self, config_info):
        return

    def get_links(self, resource_data):
        return

    def get_by_resource_id(self, resource_id,  field_list = None):
        res = json.load(requests.get('http://localhost:5001/api/user/' + resource_id).text)
        return res
