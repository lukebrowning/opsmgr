#!/usr/bin/python
#
#   Copyright 2012 iomart Cloud Services Ltd
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


import sys
import os
import subprocess

process = subprocess.Popen(["/openstack/venvs/swift-13.1.0/bin/swift-recon", "--md5"], stdout=subprocess.PIPE)

statuscode = 0
errors = []
for line in process.stdout.readlines():
    if line.find("0 error")!=-1:
        print "OK"
	sys.exit(0)

print "CRITICAL: ring md5sums do not match"
sys.exit(2)