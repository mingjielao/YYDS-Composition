from framework.rdb_data_resource import RDBDataResource

class EventTypeRDBService(RDBDataResource):

    def __init__(self, connect_info):
        super().__init__(connect_info)

    def get_next_id(self):
        sql = "select max(id) as id from event_type;"
        res = self._run_q(sql, fetch=True)
        if res[0]["id"] is None:
            res = 1
        else:
            res = res[0]["id"] + 1
        return res


