from framework.base_application_resource import BaseApplicationResource

class BaseRDBApplicationResource(BaseApplicationResource):
    def __init__(self, config_info):
        super().__init__(config_info)
