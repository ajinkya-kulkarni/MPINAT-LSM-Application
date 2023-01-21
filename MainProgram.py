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
sys.tracebacklimit = 0 # Print exception without the buit-in python warning

#############################################################################

# Clear the screen

os.system('cls||clear')
print()

#############################################################################

# Check if the PASSWORDS file exists in the current directory

file_name = "PASSWORDS.py"
file_path = os.path.join(os.getcwd(), file_name)

if not os.path.exists(file_path):
	raise Exception(f"{file_name} does not exist in the current directory")

from PASSWORDS import *

#############################################################################

# Check for package versions and update them if necessary

try:
	with open("requirements.txt") as f:
		packages = f.read().splitlines()
	subprocess.run(["pip", "install"] + packages)

	os.system('cls||clear')

except Exception as e:
	print(f"An error occurred: {e}")
	proxy = UMG_PROXY
	print(f"Trying to install packages via proxy: {proxy}")
	try:
		subprocess.run(["pip", "install", "--proxy", proxy] + packages)

		os.system('cls||clear')

	except Exception as e:
		raise Exception(f"An error occurred: {e}")
		raise Exception("Failed to install packages. Please check your proxy settings and try again.")

#############################################################################

print()

#############################################################################

# Check if the last commit is made 500 seconds back (GitHub raw content does not refresh for atleast 300 seconds)

import requests

repo_name = "MPINAT-LSM-Application"
repo_owner = "ajinkya-kulkarni"

try:
	response = requests.get(f"https://api.github.com/repos/{repo_owner}/{repo_name}", proxies=UMG_PROXY)
	data = json.loads(response.text)
	last_commit_time = data['pushed_at']
except:
	try:
		response = requests.get(f"https://api.github.com/repos/{repo_owner}/{repo_name}")
		data = json.loads(response.text)
		last_commit_time = data['pushed_at']
	except:
		raise Exception('Failed to fetch information about the latest GitHub push.')

# parse the timestamp to a datetime object
last_commit_datetime = datetime.strptime(last_commit_time, "%Y-%m-%dT%H:%M:%SZ")
# get the current time
now = datetime.utcnow()
# calculate the time elapsed
elapsed = now - last_commit_datetime

if (elapsed.seconds < 500):
	raise Warning("Application has been recently updated by the Admin(s). Please wait for 10 minutes and try again.")

#############################################################################

# Remove existing files if they exist

def check_and_delete(file_name):
	file_path = os.path.join(os.getcwd(), file_name)

	if os.path.exists(file_path):
		os.remove(file_path)
		print(f"Deleted old {file_name}")

file_names = ["LSM_StreamlitApp.py", "SanityChecks.py", "MultiPartS3Upload.py"]

for file_name in file_names:
	check_and_delete(file_name)

#############################################################################

print()

#############################################################################

# And then download them fom GitHub repo

def download_file(url, proxy=UMG_PROXY):
	"""
	Download a file from the specified URL.
	:param url: The URL of the file to download.
	:param proxy: (optional) The proxy to use for the download.
	"""
	# specify the file name
	file_name = url.split("/")[-1]
	try:
		# download the file and save it to a local file
		urllib.request.urlretrieve(url, file_name)
		print(f"Latest {file_name} fetched successfully")
	except urllib.error.HTTPError as e:
		print(f"HTTP Error: {e.code} {e.reason}")
		if proxy:
			try:
				# specify the proxy
				proxy_support = urllib.request.ProxyHandler({'http': proxy})
				opener = urllib.request.build_opener(proxy_support)
				urllib.request.install_opener(opener)
				# download the file and save it to a local file
				urllib.request.urlretrieve(url, file_name)
				print(f"Latest {file_name} fetched successfully")
			except:
				urllib.request.install_opener(None)
				print("Failed to fetch the file with proxy")
		else:
			print("Failed to fetch the file without proxy")

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
subprocess.run(['streamlit', 'run', app_path])

#############################################################################