from dump.helper import create_template_dict
from dump.match_infra import MatchRequest
from swsscommon.swsscommon import SonicDBConfig
from dash_api.route_rule_pb2 import RouteRule
from .executor import Executor

APPL_DB_SEPARATOR = SonicDBConfig.getSeparator("APPL_DB")


class Dash_Route_Rule(Executor):
    """
    Debug Dump Plugin for DASH Route Rule
    """
    ARG_NAME = "dash_route_rule_table"

    def __init__(self, match_engine=None):
        super().__init__(match_engine)
        self.is_dash_object = True

    def get_all_args(self, ns=""):
        req = MatchRequest(db="APPL_DB", table="DASH_ROUTE_RULE_TABLE", key_pattern="*", ns=ns)
        ret = self.match_engine.fetch(req)
        appliance_tables = ret["keys"]
        return [key.split(APPL_DB_SEPARATOR, 1)[1] for key in appliance_tables]

    def execute(self, params):
        self.ret_temp = create_template_dict(dbs=["APPL_DB"])
        dash_route_rule_table_name = params[self.ARG_NAME]
        self.ns = params["namespace"]
        self.init_dash_route_table_appl_info(dash_route_rule_table_name)
        return self.ret_temp

    def init_dash_route_table_appl_info(self, dash_route_rule_table_name):
        req = MatchRequest(db="APPL_DB", table="DASH_ROUTE_RULE_TABLE", key_pattern=dash_route_rule_table_name, ns=self.ns)
        ret = self.match_engine.fetch(req)
        self.add_to_ret_template(req.table, req.db, ret["keys"], ret["error"])

    def return_pb2_obj(self):
        return RouteRule()
