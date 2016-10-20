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

import logging
import socket
import time

try:
    #python 2.7
    from StringIO import StringIO
except ImportError:
    #python 3.4
    from io import StringIO

import paramiko

from opsmgr.common import constants
from opsmgr.common import exceptions
from opsmgr.common.utils import entry_exit
from opsmgr.inventory.interfaces import IManagerDevicePlugin

RHEL_RELEASE_FILE = "/etc/redhat-release"
RELEASE_TAG = "Red Hat Enterprise"

class RhelPlugin(IManagerDevicePlugin.IManagerDevicePlugin):

    PASSWORD_CHANGE_COMMAND = "passwd\n"
    PASSWORD_CHANGED_MESSAGE = "all authentication tokens updated successfully"

    def __init__(self):
        self.client = None
        self.machine_type_model = ""
        self.serial_number = ""
        self.userid = ""
        self.password = ""

    @staticmethod
    def get_type():
        return "Redhat Enterprise Linux"

    @staticmethod
    def get_web_url(host):
        return None

    @staticmethod
    def get_capabilities():
        return [constants.LOGGING_CAPABLE, constants.MONITORING_CAPABLE]

    @entry_exit(exclude_index=[0, 3, 4], exclude_name=["self", "password", "ssh_key_string"])
    def connect(self, host, userid, password=None, ssh_key_string=None):
        _method_ = "RhelPlugin.connect"
        self.userid = userid
        self.password = password
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if ssh_key_string:
                private_key = paramiko.RSAKey.from_private_key(StringIO(ssh_key_string), password)
                self.client.connect(host, username=userid, pkey=private_key, timeout=30,
                                    allow_agent=False)
            else:
                self.client.connect(host, username=userid, password=password, timeout=30,
                                    allow_agent=False)
            if not self._is_guest_rhel():
                raise exceptions.InvalidDeviceException(
                    "Device is not a RHEL Device")
        except paramiko.AuthenticationException:
            logging.error("%s::userid/password combination not valid. host=%s userid=%s",
                          _method_, host, userid)
            raise exceptions.AuthenticationException(
                "userid/password combination not valid")
        except (paramiko.ssh_exception.SSHException, OSError, socket.timeout) as e:
            logging.exception(e)
            logging.error("%s::Connection timed out. host=%s", _method_, host)
            raise exceptions.ConnectionException("Unable to ssh to the device")

    @entry_exit(exclude_index=[0], exclude_name=["self"])
    def disconnect(self):
        if self.client:
            self.client.close()

    @entry_exit(exclude_index=[0], exclude_name=["self"])
    def get_machine_type_model(self):
        return self.machine_type_model

    @entry_exit(exclude_index=[0], exclude_name=["self"])
    def get_serial_number(self):
        return self.serial_number

    @entry_exit(exclude_index=[0], exclude_name=["self"])
    def get_version(self):
        version = None
        (_stdin, stdout, _stderr) = self.client.exec_command("cat " + RHEL_RELEASE_FILE)
        for line in stdout.read().decode().splitlines():
            if line.startswith(RELEASE_TAG):
                version = line.split(' ')[6]
                break
        return version

    @entry_exit(exclude_index=[0], exclude_name=["self"])
    def get_architecture(self):
        (_stdin, stdout, _stderr) = self.client.exec_command("uname -m")
        architecture = stdout.read().decode().strip()
        return architecture

    @entry_exit(exclude_index=[0], exclude_name=["self"])
    def _is_guest_rhel(self):
        """Check the OS type is RHEL
        Return True if System is RHEL
        """
        (_stdin, stdout, _stderr) = self.client.exec_command(
            "test -e " + RHEL_RELEASE_FILE)
        rc = stdout.channel.recv_exit_status()
        return True if rc == 0 else False

    @entry_exit(exclude_index=[0, 1], exclude_name=["self", "new_password"])
    def change_device_password(self, new_password):
        """Update the password for the logged in userid.
        """

        client_shell = self.client.invoke_shell()
        client_shell.send(self.PASSWORD_CHANGE_COMMAND)
        if self.userid != "root":
            time.sleep(2)
            client_shell.send(self.password + "\n")
        time.sleep(2)
        client_shell.send(new_password + "\n")
        time.sleep(2)
        client_shell.send(new_password + "\n")
        time.sleep(5)
        output = client_shell.recv(1000).decode()
        client_shell.close()
        if self.PASSWORD_CHANGED_MESSAGE in output:
            logging.info("Password changed for " + self.userid + " successfully")
        else:
            message = "Failed to change password for %s. Console output: %s" % \
                      (self.userid, output)
            logging.warning(message)
            raise exceptions.DeviceException(message)
