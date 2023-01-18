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
import subprocess
import urllib.request

import sys
sys.dont_write_bytecode = True # Don't generate the __pycache__ folder locally

#############################################################################

# Define the proxy server

UMG_PROXY = 'http://anonymous@astaro01-proxy.med.uni-goettingen.de:8080'

#############################################################################

# First check and install packaging

try:
	subprocess.run(["pip", "show", "packaging"], check=True, stdout=subprocess.DEVNULL)
except subprocess.CalledProcessError as e:
	try:
		subprocess.run(["pip", "install", "packaging"], check=True)
	except subprocess.CalledProcessError as e:
		subprocess.run(["pip", "install", "packaging", "--proxy", UMG_PROXY], check=True)

#############################################################################

# Sheck if the PASSWORDS file exists in the current directory, else LSM_StreamlitApp.py will fail

file_name = "PASSWORDS.py"
file_path = os.path.join(os.getcwd(), file_name)

if not os.path.exists(file_path):
    raise Exception(f"{file_name} does not exist in the current directory")
else:
	print(f"{file_name} exists in the current directory")

#############################################################################

print()

#############################################################################

# Remove existing .py files if they exist

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

# Check for package versions and update them if necessary

from CheckAndInstallPackages import *

check_and_install("numpy", "1.24.1", proxy=UMG_PROXY)
check_and_install("packaging", "23.0", proxy=UMG_PROXY)
check_and_install("streamlit", "1.17.0", proxy=UMG_PROXY)
check_and_install("boto3", "1.26.50", proxy=UMG_PROXY)
check_and_install("botocore", "1.29.50", proxy=UMG_PROXY)
check_and_install("caosdb", "0.10.0", proxy=UMG_PROXY)

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