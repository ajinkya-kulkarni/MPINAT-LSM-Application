#!/usr/bin/env python3
# encoding: utf-8
#
# Copyright (C) 2022 Max Planck Institute for Multidisclplinary Sciences
# Copyright (C) 2022 University Medical Center Goettingen
# Copyright (C) 2022 Ajinkya Kulkarni <ajinkya.kulkarni@mpinat.mpg.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

#############################################################################

import os
import urllib.request
import subprocess
import json
from datetime import datetime

import sys
sys.dont_write_bytecode = True # Don't generate the __pycache__ folder locally

#############################################################################

# Clear the screen

os.system('cls||clear')

print()

#############################################################################

# Check if the PASSWORDS file exists in the current directory, else LSM_StreamlitApp.py will fail

file_name = "PASSWORDS.py"
file_path = os.path.join(os.getcwd(), file_name)

if not os.path.exists(file_path):
    raise Exception(f"{file_name} does not exist in the current directory")
else:
	print(f"{file_name} exists in the current directory")

from PASSWORDS import *

#############################################################################

# First check and install packaging

try:
	subprocess.run(["pip", "show", "packaging"], check=True, stdout=subprocess.DEVNULL)
except subprocess.CalledProcessError as e:
	try:
		subprocess.run(["pip", "install", "packaging"], check=True)
	except subprocess.CalledProcessError as e:
		subprocess.run(["pip", "install", "packaging", "--proxy", UMG_PROXY], check=True)

# Check for package versions and update them if necessary

from CheckAndInstallPackages import *

check_and_install("requests", "2.28.2", proxy=UMG_PROXY)
check_and_install("packaging", "23.0", proxy=UMG_PROXY)
check_and_install("streamlit", "1.17.0", proxy=UMG_PROXY)
check_and_install("boto3", "1.26.50", proxy=UMG_PROXY)
check_and_install("botocore", "1.29.50", proxy=UMG_PROXY)
check_and_install("caosdb", "0.10.0", proxy=UMG_PROXY)

#############################################################################

# Check if the last commit is made 10 mins back (according to GitHub cache. If yes, wait for 5 mins before passed)

import requests

repo_name = "MPINAT-LSM-Application"
repo_owner = "ajinkya-kulkarni"

try:
	response = requests.get(f"https://api.github.com/repos/{repo_owner}/{repo_name}", proxies=UMG_PROXY)
	data = json.loads(response.text)
	last_commit_time = data['pushed_at']
except:
	response = requests.get(f"https://api.github.com/repos/{repo_owner}/{repo_name}")
	data = json.loads(response.text)
	last_commit_time = data['pushed_at']

# parse the timestamp to a datetime object
last_commit_datetime = datetime.strptime(last_commit_time, "%Y-%m-%dT%H:%M:%SZ")
# get the current time
now = datetime.utcnow()
# calculate the time elapsed
elapsed = now - last_commit_datetime

if (elapsed.seconds < 600):
	raise Exception('Code updated recently. Please wait for 5 minutes.')

#############################################################################

# Remove existing files if they exist

def check_and_delete(file_name):
    file_path = os.path.join(os.getcwd(), file_name)

    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Deleted old {file_name}")

file_names = ["CheckAndInstallPackages.py",
"LSM_StreamlitApp.py", 
"ProgressPercentageCalculator.py",
"SanityChecks.py",
]

for file_name in file_names:
    check_and_delete(file_name)

# Remove ErrorLogs.txt

check_and_delete("ErrorLogs.txt")

#############################################################################

# And then download them fom GitHub repo

from DownloadURL import *

base_url = "https://raw.githubusercontent.com/ajinkya-kulkarni/MPINAT-LSM-Application/main/"

for file_name in file_names:
    url = f"{base_url}{file_name}"
    download_file(url, UMG_PROXY)

#############################################################################

print()

#############################################################################

# Run the Streamlit App

streamlit_file_name = "LSM_StreamlitApp.py"

# specify the path to the Streamlit app
app_path = os.path.join(os.getcwd(), streamlit_file_name)

os.system("echo 'Starting streamlit now...'")

print()

# run the Streamlit app with the --server.maxUploadSize flag
# For example, 5000 = 5GB
subprocess.run(["streamlit", "run", app_path, "--server.maxUploadSize=100"])

#############################################################################