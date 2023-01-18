
import os
import urllib.request
import subprocess
import packaging.version
import sys
sys.dont_write_bytecode = True # Don't generate the __pycache__ folder locally

# Define the proxy server

UMG_PROXY = 'http://anonymous@astaro01-proxy.med.uni-goettingen.de:8080'

#############################################################################

os.system('cls||clear')

print()

#############################################################################

# check if the PASSWORDS file exists in the current directory

file_name = "PASSWORDS.py"
file_path = os.path.join(os.getcwd(), file_name)

if not os.path.exists(file_path):
    raise Exception(f"{file_name} does not exist in the current directory")
else:
	print(f"{file_name} exists in the current directory")

#############################################################################

print()

#############################################################################

file_names = ["LSM_StreamlitApp.py", 
"SanityChecks.py", 
"ProgressPercentageCalculator.py",
"CheckAndDeleteFiles.py", 
"CheckAndInstallPackages.py",
"DownloadURL.py",
]

for file_name in file_names:
    module_name.check_and_delete(file_name)

#############################################################################

# specify the file names to download

base_url = "https://raw.githubusercontent.com/ajinkya-kulkarni/MPINAT-LSM-Application/main/"

for file_name in file_names:
    url = f"{base_url}{file_name}"
    download_file(url, UMG_PROXY)

#############################################################################

print()

#############################################################################

check_and_install("packaging", "23.0", proxy=UMG_PROXY)
check_and_install("streamlit", "1.17.0", proxy=UMG_PROXY)
check_and_install("boto3", "1.26.50", proxy=UMG_PROXY)
check_and_install("botocore", "1.29.50", proxy=UMG_PROXY)
check_and_install("caosdb", "0.10.0", proxy=UMG_PROXY)

#############################################################################

print()

#############################################################################

# specify the file name
streamlit_file_name = "LSM_StreamlitApp.py"

# specify the path to the Streamlit app
app_path = os.path.join(os.getcwd(), streamlit_file_name)

os.system("echo 'Starting streamlit now...'")

print()

# run the Streamlit app with the --server.maxUploadSize flag
# 5000 = 5GB
subprocess.run(["streamlit", "run", app_path, "--server.maxUploadSize=100"])

#############################################################################
