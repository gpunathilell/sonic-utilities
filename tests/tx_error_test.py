import os
import sys
import json
import pytest

from click.testing import CliRunner
import config.main as config
import show.main as show
from utilities_common.db import Db
from .tx_error_input.tx_error_test_vectors import *

test_path = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(test_path)
scripts_path = os.path.join(modules_path, "scripts")
sys.path.insert(0, test_path)
sys.path.insert(0, modules_path)

class TestTxErrorConfig(object): 
    @classmethod
    def setup_class(cls):
        os.environ["PATH"] += os.pathsep + scripts_path
        os.environ['UTILITIES_UNIT_TESTING'] = "2"
        print("SETUP")

    def test_tx_error_config(self):
        self.executor(testData['tx_error_config'])

    def test_tx_error_config_error(self):
        self.executor(testData['tx_error_show'])

    def test_tx_error_show(self):
        self.executor(testData['test_tx_error_config_error'])

    def test_tx_error_config_interface(self):
        self.executor(testData['test_tx_error_set_config_interface'])

    def test_tx_error_clear_interface(self):
        self.executor(testData['test_tx_error_clear_config_interface'])
    
    def test_tx_error_clear_interface_error(self):
        self.executor(testData['test_tx_error_clear_config_error'])
    
    def executor(self, input):
        runner = CliRunner()
        if 'db_table' in input:
            db = Db()
            data_list = list(db.cfgdb.get_table(input['db_table']))
            input['rc_output'] = input['rc_output'].format(",".join(data_list))
        if 'show' in input['cmd']:
            exec_cmd = show.cli.commands["interfaces"].commands["tx_error"]
        elif 'config' in input['cmd']:
            exec_cmd = config.config.commands["tx_error_stat_poll_period"]
        elif 'tx_error_set' in input['cmd']:
            exec_cmd = config.config.commands["interface"].commands["tx_error_threshold"].commands["set-thresh"]
        elif 'tx_error_clear' in input['cmd']:
            exec_cmd = config.config.commands["interface"].commands["tx_error_threshold"].commands["clear-thresh"]
        elif 'tx_error_clear' in input['cmd']:
            exec_cmd = config.config.commands["interface"].commands["tx_error_threshold"].commands["clear-thresh"]
        elif 'tx_error_clear_error' in input['cmd']:
            exec_cmd = config.config.commands["interface"].commands["tx_error_threshold"].commands["clear-thresh"]
        if 'args' in input.keys():
            result = runner.invoke(exec_cmd, input['args'], catch_exceptions=False)
        else:
            result = runner.invoke(exec_cmd, catch_exceptions=False)
        exit_code = result.exit_code
        output = result.output
        print("{} is the output".format(output))
        if input['rc'] == 0:
            assert exit_code == 0
        else:
            assert exit_code != 0
        if 'rc_msg' in input:
            assert input['rc_msg'] == output
        if 'rc_output' in input:
            assert output == input['rc_output']
    
    @classmethod
    def teardown_class(cls):
        os.environ["PATH"] = os.pathsep.join(os.environ["PATH"].split(os.pathsep)[:-1])
        os.environ['UTILITIES_UNIT_TESTING'] = "0"


        
