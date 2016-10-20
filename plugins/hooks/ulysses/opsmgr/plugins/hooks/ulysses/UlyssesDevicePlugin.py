# Copyright 2016, IBM US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

try:
    #python 2.7
    from StringIO import StringIO
except ImportError:
    #python 3.4
    from io import StringIO
import paramiko
from opsmgr.inventory.interfaces.IManagerDeviceHook import IManagerDeviceHook
from opsmgr.inventory import resource_mgr, persistent_mgr
from opsmgr.common.utils import entry_exit

class UlyssesDevicePlugin(IManagerDeviceHook):

    ROLE_FILE = "/etc/roles"

    @staticmethod
    def add_device_pre_save(device):
        pass

    @staticmethod
    def remove_device_pre_save(device):
        pass

    @staticmethod
    def change_device_pre_save(device, old_device_info):
        pass

    @staticmethod
    @entry_exit(exclude_index=[], exclude_name=[])
    def add_device_post_save(device):
        if device.resource_type == "Ubuntu":
            address = device.address
            userid = device.userid
            key = device.key
            if key:
                key_string = key.value
                if key.password is not None:
                    password = persistent_mgr.decrypt_data(key.password)
                else:
                    password = None
            else:
                key_string = None
                password = persistent_mgr.decrypt_data(device.password)
            client = UlyssesDevicePlugin._connect(address, userid, password, key_string)
            roles = []
            command = "cat " + UlyssesDevicePlugin.ROLE_FILE
            (_stdin, stdout, _stderr) = client.exec_command(command)
            for line in stdout.read().decode().splitlines():
                roles.append(line.strip())
            resource_mgr.add_resource_roles(device.resource_id, roles)

    @staticmethod
    def remove_device_post_save(device):
        pass

    @staticmethod
    def change_device_post_save(device, old_device_info):
        pass

    @staticmethod
    def _connect(host, userid, password, ssh_key_string=None):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if ssh_key_string:
            private_key = paramiko.RSAKey.from_private_key(StringIO(ssh_key_string), password)
            client.connect(host, username=userid, pkey=private_key, timeout=30,
                           allow_agent=False)
        else:
            client.connect(host, username=userid, password=password, timeout=30,
                           allow_agent=False)
        return client
