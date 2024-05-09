from dump.helper import create_template_dict
from dump.match_infra import MatchRequest
from swsscommon.swsscommon import SonicDBConfig
import dash_api
from dash_api.acl_group_pb2 import AclGroup
from dump.match_helper import fetch_acl_counter_oid
from .executor import Executor
import redis
from dump.match_infra import JsonSource, MatchEngine, CONN
from google.protobuf.json_format import MessageToDict


APPL_DB_SEPARATOR = SonicDBConfig.getSeparator("APPL_DB")

class Dash_Acl_Group(Executor):
    """
    Debug Dump Plugin for DASH ACL Group
    """
    ARG_NAME = "dash_acl_group_table"

    def __init__(self, match_engine=None):
        super().__init__(match_engine)
        self.is_dash_object = True

    def get_all_args(self, ns=""):
        req = MatchRequest(db="APPL_DB", table="DASH_ACL_GROUP_TABLE", key_pattern="*", ns=ns)
        ret = self.match_engine.fetch(req)
        appliance_tables = ret["keys"]
        print(f"{ret['keys']} are the keys")
        return [key.split(APPL_DB_SEPARATOR)[-1] for key in appliance_tables]

    def execute(self, params):
        self.ret_temp = create_template_dict(dbs=["APPL_DB"])
        dash_app_table_name = params[self.ARG_NAME]
        print(f"{params} and {dash_app_table_name}")
        self.ns = params["namespace"]
        self.init_dash_app_table_config_info(dash_app_table_name)
        return self.ret_temp

    def init_dash_app_table_config_info(self, dash_app_table_name):
        req = MatchRequest(db="APPL_DB", table="DASH_ACL_GROUP_TABLE", key_pattern=dash_app_table_name, return_fields=["type"], ns=self.ns)
        ret = self.match_engine.fetch(req)
        self.add_to_ret_template(req.table, req.db, ret["keys"], ret["error"])

    def return_pb2_obj(self):
        return AclGroup()