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
from datetime import datetime, timedelta

import sys
sys.dont_write_bytecode = True # Don't generate the __pycache__ folder locally
sys.tracebacklimit = 0 # Print exception without the buit-in python warning

#############################################################################

# Check if the PASSWORDS file exists in the current directory

file_name = "PASSWORDS.py"
file_path = os.path.join(os.getcwd(), file_name)

if not os.path.exists(file_path):
	raise Exception(f"{file_name} does not exist in the current directory")

from PASSWORDS import *

#############################################################################

# Check if the last commit is made 500 seconds back (GitHub raw content does not refresh for atleast 300 seconds)

repo_name = "MPINAT-LSM-Application"
repo_owner = "ajinkya-kulkarni"

try:
	# send an HTTP GET request to the GitHub API to retrieve information about the latest push
	url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
	request = urllib.request.Request(url)
	request.add_header('User-Agent', 'Mozilla/5.0')
	response = urllib.request.urlopen(request)
	data = json.loads(response.read())
	last_commit_time = data['pushed_at']
except:
	try:
		# try again without a proxy
		response = urllib.request.urlopen(url)
		data = json.loads(response.read())
		last_commit_time = data['pushed_at']
	except:
		raise Exception('Failed to fetch information about the latest GitHub push.')

# parse the timestamp to a datetime object
last_commit_datetime = datetime.strptime(last_commit_time, "%Y-%m-%dT%H:%M:%SZ")
# get the current time
now = datetime.utcnow()
# calculate the time elapsed
elapsed = now - last_commit_datetime

if elapsed.total_seconds() < 500:
	remaining_time = timedelta(seconds=500) - elapsed
	raise Exception(f"Application has been recently updated by the Admin(s). Please wait for {remaining_time.total_seconds()} seconds and try again.")

#############################################################################

# Delete all files/folder except PASSWORDS.py

def delete_file(file_name, file_path):
	"""
	Delete the specified file if it exists in the current working directory.
	:param file_name: The name of the file to delete.
	"""
	try:
		os.remove(file_path)
		print(f"Deleted old {file_name}")
	except:
		pass

#########

file_names = ["LSM_StreamlitApp.py", "modules.py", "requirements.txt"]

for file_name in file_names:

	file_path = os.path.join(os.getcwd(), file_name) # Get the current directory

	delete_file(file_name, file_path)

#############################################################################

# Download files fom GitHub repo

def download_file(url, proxy=None):
	"""
	Download a file from the specified URL.

	:param url: The URL of the file to download.
	:param proxy: (optional) The proxy to use for the download.
	:raises ValueError: If the URL is invalid or the download fails.
	"""
	try:
		# Validate the URL
		if not url.startswith("http"):
			raise ValueError("Invalid URL: " + url)

		# Set up the request with a User-Agent header to avoid 403 errors
		headers = {"User-Agent": "Mozilla/5.0"}
		request = urllib.request.Request(url, headers=headers)

		# Create a proxy handler if a proxy is specified
		if proxy:
			proxy_handler = urllib.request.ProxyHandler({"http": proxy})
			opener = urllib.request.build_opener(proxy_handler)
		else:
			opener = urllib.request.build_opener()

		# Open the URL using the opener
		response = opener.open(request)

		# Read the response and write to a file
		with open(os.path.basename(url), "wb") as file:
			file.write(response.read())

		print(f"Downloaded {os.path.basename(url)} successfully")

	except (urllib.error.URLError, ValueError) as e:
		raise ValueError(f"Failed to download file from {url}: {e}") from e
	except Exception as e:
		raise ValueError(f"Failed to download file from {url}") from e

#########

file_names = ["LSM_StreamlitApp.py", "modules.py", "requirements.txt"]

base_url = "https://raw.githubusercontent.com/ajinkya-kulkarni/MPINAT-LSM-Application/main/"

for file_name in file_names:
	url = f"{base_url}{file_name}"
	download_file(url, UMG_PROXY)

#############################################################################

# Check for package versions and update them if necessary

try:
	with open("requirements.txt") as f:
		packages = f.read().splitlines()
	subprocess.run(["pip", "install"] + packages)

except Exception as e:
	print(f"An error occurred: {e}")
	proxy = UMG_PROXY
	print(f"Trying to install packages via proxy: {proxy}")
	try:
		subprocess.run(["pip", "install", "--proxy", proxy] + packages)

	except Exception as e:
		raise Exception(f"An error occurred: {e}")

#############################################################################

from modules import *

# Make the LSM_overview.csv file
make_LSM_overview(LINKAHEAD_URL, LINKAHEAD_USERNAME, LINKAHEAD_PASSWORD, UMG_PROXY)

#############################################################################

# Run the Streamlit App

streamlit_file_name = "LSM_StreamlitApp.py"

# specify the path to the Streamlit app
app_path = os.path.join(os.getcwd(), streamlit_file_name)

os.system("echo 'Starting streamlit now...'")

# run the Streamlit app
subprocess.run(['streamlit', 'run', app_path])

#############################################################################
