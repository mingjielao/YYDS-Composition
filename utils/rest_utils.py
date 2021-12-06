import copy
from flask import request
import json
import logging
from datetime import datetime

logger = logging.getLogger()


class RESTContext:
    _default_limit = 10

    def __init__(self, request_context, path_parameters=None):
        log_message = ""
        self.limit = RESTContext._default_limit

        self.path = request_context.path
        args = dict(request_context.args)

        args = self._de_array_args(args)
        self.path = request.path

        # self.filtered_args()

        self.data = None
        self.headers = dict(request.headers)
        self.method = request.method
        self.host_url = request.host_url
        self.full_path = request.full_path
        self.base_url = request.base_url
        self.url = request.url

        self.path_parameter = path_parameters

        try:
            self.data = request_context.get_json()
        except Exception as e:
            pass

        args, limit = self._get_and_remove_arg(args, "limit")
        self.limit = limit

        args, offset = self._get_and_remove_arg(args, "offset")
        self.offset = offset

        args, order_by = self._get_and_remove_arg(args, "order_by")
        self.order_by = order_by

        args, fields = self._get_and_remove_arg(args, "fields")

        if fields is not None:
            fields = fields.split(",")

        self.fields = fields

        self.args = args

    @staticmethod
    def _de_array_args(args):
        result = {}

        if args is not None:
            for k,v in args.items():
                if type(v) == list:
                    result[k] = ",".join(v)
                else:
                    result[k] = v

        return result

    @staticmethod
    def _get_and_remove_arg(args, arg_name):
        val = copy.copy(args.get(arg_name, None))
        if val is not None:
            del args[arg_name]

        return args, val

    def filtered_args(self):

        if "limit" in self.args:
            self.limit = self.args.get("limit")
            self.args.pop("limit")

        if "offset" in self.args:
            self.args.pop("offset")

    def add_pagination(self, response_data):
        pass
