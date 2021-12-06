from framework.base_application_resource import BaseApplicationResource

class EventResource(BaseApplicationResource):

    def __init__(self, config_info):
        super().__init__(config_info)

    def get_links(self, resource_data):
        for r in resource_data:
            event_id = r.get('id')
            organizer_id = r.get('organizer_id')
            type_id = r.get('type_id')
            venue_id = r.get('venue_id')

            links = []
            self_link = {"rel": "self", "href": "/api/event/" + str(event_id)}
            links.append(self_link)

            organizer_link = {"rel": "organizer", "href": "/api/user/" + str(organizer_id)}
            links.append(organizer_link)

            type_link = {"rel": "type", "href": "/api/eventtype/" + str(type_id)}
            links.append(type_link)

            venue_link = {"rel": "venue", "href": "/api/eventvenue/" + str(venue_id)}
            links.append(venue_link)

            r["links"] = links

        return resource_data

    def create(self, new_resource_info):
        db_svc = self._get_db_resource()
        if "starttime" not in new_resource_info or "endtime" not in new_resource_info or "organizer_id" not in new_resource_info:
            return -1
        next_id = db_svc.get_next_id()
        new_resource_info["id"] = next_id
        res = super().create(new_resource_info)

        if res == 1:
            res = {}
            res["location"] = "/api/event/" + str(next_id)
        return res
