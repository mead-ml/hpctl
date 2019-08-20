from __future__ import absolute_import, division, print_function, unicode_literals

import os
import glob
import json
import socket
import getpass
from baseline.utils import read_config_file
from baseline.utils import export as exporter
from xpctl import xpctl_client
from xpctl.utils import to_swagger_experiment



__all__ = []
export = exporter(__all__)


def read_logs(file_name):
    logs = []
    with open(file_name) as f:
        for line in f:
            logs.append(json.loads(line))
    return logs


def dummy_print(s):
    pass


@export
class XPCTL(object):
    def __init__(self, label=None, **kwargs):
        super(XPCTL, self).__init__()
        self.name = label
        self.xpctl = xpctl_client(kwargs['host'])
        self.username = kwargs.get('user', getpass.getuser())
        self.hostname = kwargs.get('host', socket.gethostname())

    def put_result(self, label):
        # Wait to create the experiment repo until after the fork
        loc = os.path.join(label.exp, label.sha1, label.name)
        config_loc = os.path.join(loc, 'config.json')
        config = read_config_file(config_loc)
        task = config.get('task')
        log_loc = glob.glob(os.path.join(loc, 'reporting-*.log'))[0]
        logs = read_logs(log_loc)
        result = self.xpctl.put_result(
            task,
            to_swagger_experiment(
                task,
                config,
                logs,
                username=self.username,
                hostname=self.hostname,
                label=self.name,
            )
        )
        return result.message


@export
def get_xpctl(xpctl_config):
    if xpctl_config is None:
        return None
    if xpctl_config.pop('type', 'local') == 'remote':
        from hpctl.remote import RemoteXPCTL
        return RemoteXPCTL(**xpctl_config)
    return XPCTL(**xpctl_config)
