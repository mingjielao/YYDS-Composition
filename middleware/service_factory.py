import middleware.context as context

from application_services.EventResource.event_application_service import EventResource
from application_services.EventTypeResource.eventtype_application_service import EventTypeResource
from application_services.EventVenueResource.eventvenue_application_service import EventVenueResource
from application_services.EventOrganizerResource.eventorganizer_application_service import EventOrganizerResource
from database_services.event_rdb_service import EventRDBService
from database_services.eventtype_rdb_service import EventTypeRDBService
from database_services.eventvenue_rdb_service import EventVenueRDBService

class ServiceFactory:

    def __init__(self):
        self.db_connect_info = context.get_db_info()
        e_svc = EventRDBService(self.db_connect_info)
        et_svc = EventTypeRDBService(self.db_connect_info)
        ev_svc = EventVenueRDBService(self.db_connect_info)

        self.services = {}

        event_svc_config_info = {
            "db_resource": e_svc,
            "db_table_name": "event",
            "key_columns": ["id"]
        }
        event_svc = EventResource(event_svc_config_info)

        self.services["event"] = event_svc

        eventorganizer_svc_config_info = {}
        eventorganizer_svc = EventOrganizerResource(eventorganizer_svc_config_info)

        self.services["eventorganizer"] = eventorganizer_svc

        eventtype_svc_config_info = {
            "db_resource": et_svc,
            "db_table_name": "event_type",
            "key_columns": ["id"]
        }
        eventtype_svc = EventTypeResource(eventtype_svc_config_info)

        self.services["eventtype"] = eventtype_svc

        eventvenue_svc_config_info = {
            "db_resource": ev_svc,
            "db_table_name": "event_venue",
            "key_columns": ["id"]
        }
        eventvenue_svc = EventVenueResource(eventvenue_svc_config_info)

        self.services["eventvenue"] = eventvenue_svc

    def get_service(self, service_name):
        result = self.services.get(service_name, None)
        return result
