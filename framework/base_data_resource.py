from abc import ABC, abstractmethod


class BaseDataException(Exception):
    def __init__(self):
        pass


class BaseDataResource(ABC):

    def __init__(self, connect_info):
        self.connect_info = connect_info

    @abstractmethod
    def find_by_template(self, resource_name, template, fields, limit, offset):
        pass

    @abstractmethod
    def create(self, resource_name, new_resource_data):
        pass
