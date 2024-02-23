show_tx_error_config = """\
Port    status    statistics
------  --------  ------------
"""

error_tx_config = """\
Usage: tx_error_stat_poll_period [OPTIONS] <period>
Try "tx_error_stat_poll_period --help" for help.

Error: Invalid value for "<period>": No is not a valid integer
"""

error_tx_config_int = """\
Usage: clear-thresh [OPTIONS] <interface_name>
Try "clear-thresh --help" for help.

Error: Tx Error threshold hasn't been configured on the interface
"""

testData = {
             'tx_error_show' : {'cmd' : ['show'],
                                    'rc' : 0,
                                    'rc_output': show_tx_error_config
                                },
             'tx_error_config' : {'cmd' : ['config'],
                                   'args' : ['50'],
                                   'rc' : 0,
                                  },
             'test_tx_error_config_error' :    {'cmd' : ['config'],
                                   'args' : ['No'],
                                   'rc' : 2,
                                   'rc_msg' : error_tx_config
                                  },
              'test_tx_error_set_config_interface' :    {'cmd' : ['tx_error_set'],
                                   'args' : ['Ethernet0','20'],
                                   'rc' : 0,
                                  },
               'test_tx_error_clear_config_interface' :    {'cmd' : ['tx_error_clear'],
                                   'args' : ['Ethernet0'],
                                   'rc' : 0,
                                  },
               'test_tx_error_clear_config_error' :    {'cmd' : ['tx_error_clear_error'],
                                   'args' : ['Ethernet4'],
                                   'rc' : 2,
                                   'rc_msg' : error_tx_config_int,
                                  }
           }
