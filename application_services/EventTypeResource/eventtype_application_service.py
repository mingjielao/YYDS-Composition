from framework.base_application_resource import BaseApplicationResource

class EventTypeResource(BaseApplicationResource):

    def __init__(self, config_info):
        super().__init__(config_info)

    def get_links(self, resource_data):
        for r in resource_data:
            type_id = r.get('id')

            links = []
            self_link = {"rel": "self", "href": "/api/eventtype/" + str(type_id)}
            links.append(self_link)

            r["links"] = links

        return resource_data

    def create(self, new_resource_info):
        db_svc = self._get_db_resource()
        if "name" not in new_resource_info:
            return -1
        next_id = db_svc.get_next_id()
        new_resource_info["id"] = next_id
        res = super().create(new_resource_info)

        if res == 1:
            res = {}
            res["location"] = "/api/eventtype/" + str(next_id)

        return res
