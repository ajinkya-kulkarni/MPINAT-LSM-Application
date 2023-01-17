
import os
import urllib.request
import subprocess
import packaging.version
import sys
sys.dont_write_bytecode = True # Don't generate the __pycache__ folder locally

#############################################################################

os.system('cls||clear')

subprocess.run("echo.", shell=True)

#############################################################################

# check if the PASSWORDS file exists in the current directory
file_name = "PASSWORDS.py"
file_path = os.path.join(os.getcwd(), file_name)

if not os.path.exists(file_path):
    raise Exception(f"{file_name} does not exist in the current directory")
else:
	print(f"{file_name} exists in the current directory")

#############################################################################

# define the proxy server from the PASSWORDS file

from PASSWORDS import *

#############################################################################

subprocess.run("echo.", shell=True)

#############################################################################

# specify the file name
file_name = "LSM_StreamlitApp.py"

# check if the file already exists in the current directory and delete it before downloading it again

file_path = os.path.join(os.getcwd(), file_name)

if os.path.exists(file_path):
	os.remove(file_path)
	print(f"Deleted old {file_name}")

#############################################################################

# specify the url of the file you want to download
url = "https://raw.githubusercontent.com/ajinkya-kulkarni/MPINAT-LSM-Application/main/LSM_StreamlitApp.py"

# download the "LSM_StreamlitApp.py" file, first without a proxy and then with a proxy
try:
    # download the file and save it to a local file
    urllib.request.urlretrieve(url, file_name)
    print(f"Latest {file_name} fetched successfully")

except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} {e.reason}")
    try:
        # specify the proxy
        proxy_support = urllib.request.ProxyHandler({'http': UMG_PROXY})
        opener = urllib.request.build_opener(proxy_support)
        urllib.request.install_opener(opener)
        # download the file and save it to a local file
        urllib.request.urlretrieve(url, file_name)
        print(f"Latest {file_name} fetched successfully")
    except:
        urllib.request.install_opener(None)
        print("Failed to fetch the file with proxy and without proxy")
except:
    print("Failed to fetch the file without proxy")

#############################################################################

subprocess.run("echo.", shell=True)

#############################################################################

# function to check for latest versions
def check_and_install(package_name, version, proxy=None):
    try:
        current_version = subprocess.check_output(["pip", "show", package_name]).decode("utf-8").split("\n")
        current_version = [line.split(":")[1].strip() for line in current_version if "Version" in line][0]
        latest_version = subprocess.check_output(["pip", "show", "-v", package_name]).decode("utf-8").split("\n")
        latest_version = [line.split(":")[1].strip() for line in latest_version if "Version" in line][0]
        if packaging.version.parse(current_version) < packaging.version.parse(version):
            if proxy:
                subprocess.run(["pip", "install", "--upgrade", "--proxy", proxy, package_name], check=True)
            else:
                subprocess.run(["pip", "install", "--upgrade", package_name], check=True)
            print(f"{package_name} package installed successfully")
        else:
            print(f"{package_name} package version is already >= {version}")
    except subprocess.CalledProcessError as e:
        try:
            if proxy:
                subprocess.run(["pip", "install", "--upgrade", "--proxy", proxy, package_name], check=True)
            else:
                subprocess.run(["pip", "install", "--upgrade", package_name], check=True)
            print(f"{package_name} package installed successfully")
        except subprocess.CalledProcessError as e:
            print("Error: Failed to install {package_name} package")
            print("Error code: ", e.returncode)
            print("Error message: ", e.output)

check_and_install("packaging", "23.0")
check_and_install("streamlit", "1.17.0")
check_and_install("boto3", "1.26.50")
check_and_install("botocore", "1.29.50")
check_and_install("caosdb", "0.10.0")

#############################################################################

subprocess.run("echo.", shell=True)

#############################################################################

# specify the path to the Streamlit app
app_path = os.path.join(os.getcwd(), file_name)

os.system("echo 'Starting streamlit now...'")

subprocess.run("echo.", shell=True)

# run the Streamlit app with the --server.maxUploadSize flag
# 5000 = 5GB
subprocess.run(["streamlit", "run", app_path, "--server.maxUploadSize=100"])

#############################################################################
