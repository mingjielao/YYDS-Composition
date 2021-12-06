from abc import ABC, abstractmethod


class BaseApplicationException(Exception):

    def __init__(self):
        pass


class BaseApplicationResource(ABC):

    def __init__(self, config_info):
        self._db_resource = config_info.get("db_resource", None)
        self._db_table_name = config_info.get("db_table_name", None)
        self._key_columns = config_info.get("key_columns", None)

    def get_by_template(self, template=None, field_list=None, limit=None, offset=None):
        db_resource = self._get_db_resource()
        db_table_name = self._get_db_table_name()

        if limit is None or int(limit) > 20:
            limit = "20"
        if offset is None:
            offset = "0"

        res = db_resource.find_by_template(db_table_name, template, field_list, limit, offset)
        res = self.get_links(res)

        result = {}
        result['data'] = res

        links = []
        self_link = {"rel": "self", "href": "/api/"+db_table_name+"?" + self.getTemplateLink(template) + self.getFieldListLink(field_list) + self.getPagination(limit, offset)}
        links.append(self_link)

        next_link = {"rel": "next", "href": "/api/"+db_table_name+"?" + self.getTemplateLink(template) + self.getFieldListLink(field_list) + self.getPagination(limit, str(int(offset)+int(limit)))}
        links.append(next_link)

        if int(offset)-int(limit) >= 0:
            prev_link = {"rel": "prev", "href": "/api/"+db_table_name+"?" + self.getTemplateLink(template) + self.getFieldListLink(field_list) + self.getPagination(limit, str(int(offset)-int(limit)))}
            links.append(prev_link)

        result['links'] = links
        return result

    def create(self, new_resource_data):
        db_resource = self._get_db_resource()
        db_table_name = self._get_db_table_name()
        res = db_resource.create(db_table_name, new_resource_data)

        return res

    def get_by_resource_id(self, resource_id, field_list):
        db_resource = self._get_db_resource()
        db_table_name = self._get_db_table_name()

        template = self.get_template(resource_id)

        res = db_resource.get_by_attribute(db_table_name, template, field_list)
        res = self.get_links(res)
        return res

    def delete_by_resource_id(self, resource_id):
        db_resource = self._get_db_resource()
        db_table_name = self._get_db_table_name()

        template = self.get_template(resource_id)

        res = db_resource.delete_by_attribute(db_table_name, template)
        return res

    def put_by_resource_id(self, resource_id, update_data):
        db_resource = self._get_db_resource()
        db_table_name = self._get_db_table_name()

        template = self.get_template(resource_id)

        res = db_resource.put_by_attribute(db_table_name, template, update_data)
        return res

    def get_data_resource_info(self):
        pass

    @abstractmethod
    def get_links(self, resource_data):
        pass

    def get_template(self, values):
        template = {}
        values = values.split("&")
        for field, value in zip(self._get_key_columns(), values):
            template[field] = value
        return template

    def _get_db_resource(self):
        result = self._db_resource
        return result

    def _get_db_table_name(self):
        result = self._db_table_name
        return result

    def _get_key_columns(self):
        result = self._key_columns
        return result

    def getTemplateLink(self, template):
        result = ""
        if template is not None and template != {}:
            for k, v in template.items():
                result += k + "="
                result += v + "&"
        return result

    def getFieldListLink(self, field_list):
        result = ""
        if field_list is not None:
            result += "fields=" + ",".join(field_list)
        return result

    def getPagination(self, limit, offset):
        return "&limit="+ limit + "&offset=" + offset