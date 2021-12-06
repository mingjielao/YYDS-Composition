import pymysql
import logging

import middleware.context as context
from framework.base_data_resource import BaseDataResource

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class RDBDataResource(BaseDataResource):
    def __init__(self, connect_info):
        connect_info["cursorclass"] = pymysql.cursors.DictCursor
        connect_info["autocommit"] = True
        super().__init__(connect_info)

    @staticmethod
    def _get_db_connection():
        db_connect_info = context.get_db_info()

        logger.info("RDBService._get_db_connection:")
        logger.info("\t HOST = " + db_connect_info['host'])

        db_info = context.get_db_info()

        db_connection = pymysql.connect(
            **db_info,
            autocommit=True
        )
        return db_connection

    # @classmethod
    # def get_by_prefix(cls, column_name, value_prefix):
    #
    #     conn = RDBService._get_db_connection()
    #     cur = conn.cursor()
    #
    #     sql = "select * from " + cls.db_schema + "." + cls.table_name + " where " + \
    #           column_name + " like " + "'" + value_prefix + "%'"
    #     print("SQL Statement = " + cur.mogrify(sql, None))
    #
    #     res = cur.execute(sql)
    #     res = cur.fetchall()
    #
    #     conn.close()
    #
    #     return res

    def get_by_attribute(self, db_resource, template, field_list):
        wc, args = self._get_where_clause_args(template)
        proj = self._get_project_terms(field_list)

        sql = "select " + proj + " from " + db_resource + wc
        res = self._run_q(sql, args, fetch=True)
        return res

    def delete_by_attribute(self, db_resource, template):
        wc, args = self._get_where_clause_args(template)

        sql = "delete from " + db_resource + wc

        res = self._run_q(sql, args, fetch=True)
        return res

    def put_by_attribute(self, db_resource, template, update_data):
        wc, args = self._get_where_clause_args(template)

        sql = "UPDATE " + db_resource + " SET "
        sql = sql + " , ".join([ k + "= '"+ v + "'" for k,v in update_data.items()])

        sql = sql + wc
        res = self._run_q(sql, args, fetch=True)

        return res

    @classmethod
    def get_where_clause_args(cls, template):
        terms = []
        args = []
        clause = None

        if template is None or template == {}:
            clause = ""
            args = None
        else:
            for k, v in template.items():
                terms.append(k + "=%s")
                args.append(v)

            clause = " where " + " AND ".join(terms)

        return clause, args

    def find_by_template(self, resource_name, template=None, field_list=None, limit=None, offset=None):

        wc, args = self._get_where_clause_args(template)
        proj = self._get_project_terms(field_list)

        sql = "select " + proj + " from " + resource_name + " " + wc

        sql += " limit " + str(limit)
        sql += " offset " + str(offset)

        res = self._run_q(sql, args, fetch=True)

        return res

    def create(self, resource_name, new_resource_data):
        sql = "insert into " + resource_name

        cols = []
        vals = []
        args = []

        for k, v in new_resource_data.items():
            cols.append(k)
            vals.append('%s')
            args.append(v)

        sql += " (" + ",".join(cols) + ") "
        sql += " values(" + ",".join(vals) + ") "

        res = self._run_q(sql, args, fetch=False)
        return res

    def _get_where_clause_args(self, template):
        if template is None or template == {}:
            wc, args = "", None
        else:
            args = []
            terms = []

            for k,v in template.items():
                tmp = k + "=%s"
                terms.append(tmp)
                args.append(v)

            wc = " where " + " and ".join(terms)
        return wc, args

    def _get_project_terms(self, field_list):
        if field_list is None or len(field_list) == 0:
            result = " * "
        else:
            result = " " + ",".join(field_list) + " "
        return result

    def _get_connection(self):
        conn = pymysql.connect(**self.connect_info)
        return conn

    def _run_q(self, sql, args=None, fetch=False):
        conn = self._get_connection()
        cur = conn.cursor()

        full_sql = cur.mogrify(sql, args)
        logger.debug("rdb_data_resource._run_q: SQL = " + full_sql)

        res = cur.execute(sql, args)
        if fetch:
            res = cur.fetchall()

        conn.close()
        return res