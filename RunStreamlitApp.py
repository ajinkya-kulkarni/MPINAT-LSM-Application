
import os
import urllib.request
import subprocess
import packaging.version

#############################################################################

os.system('cls||clear')

#############################################################################

# define the proxy server
UMG_PROXY = 'http://anonymous@astaro01-proxy.med.uni-goettingen.de:8080'

#############################################################################

# check if the PASSWORDS file exists in the current directory
file_name = "PASSWORDS.py"
file_path = os.path.join(os.getcwd(), file_name)

if not os.path.exists(file_path):
    raise Exception(f"{file_name} does not exist in the current directory")

#############################################################################

# get the current directory path
directory_path = os.getcwd()

#############################################################################

# specify the file name
file_name = "LSM_StreamlitApp.py"

#############################################################################

# specify the url of the file you want to download
url = "https://raw.githubusercontent.com/ajinkya-kulkarni/MPINAT-LSM-Application/main/LSM_StreamlitApp.py"

#############################################################################

# check if the file already exists in the current directory and delete it before downloading it again

file_path = os.path.join(os.getcwd(), file_name)

if os.path.exists(file_name):
	os.remove(file_name)

#############################################################################

os.system("echo ''")

#############################################################################

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

os.system("echo ''")

# specify the path to the Streamlit app
app_path = os.path.join(os.getcwd(), file_name)

#############################################################################

# Check if streamlit >= 1.17.0, if not download latest version
try:
	current_version = subprocess.check_output(["pip", "show", "streamlit"]).decode("utf-8").split("\n")
	current_version = [line.split(":")[1].strip() for line in current_version if "Version" in line][0]
	latest_version = subprocess.check_output(["pip", "show", "-v", "streamlit"]).decode("utf-8").split("\n")
	latest_version = [line.split(":")[1].strip() for line in latest_version if "Version" in line][0]
	if packaging.version.parse(current_version) < packaging.version.parse("1.17.0"):
		subprocess.run(["pip", "install", "--upgrade", "streamlit"], check=True)
		print("streamlit package installed successfully")
	else:
		print("streamlit package version is already >= 1.17.0")
except subprocess.CalledProcessError as e:
	try:
		subprocess.run(["pip", "install", "--upgrade", "--proxy", UMG_PROXY, "streamlit"], check=True)
		print("streamlit package installed successfully")
	except subprocess.CalledProcessError as e:
		print("Error: Failed to install streamlit package")
		print("Error code: ", e.returncode)
		print("Error message: ", e.output)

# Check if boto3 > 1.26.50, if not download latest version
try:
	current_version = subprocess.check_output(["pip", "show", "boto3"]).decode("utf-8").split("\n")
	current_version = [line.split(":")[1].strip() for line in current_version if "Version" in line][0]
	latest_version = subprocess.check_output(["pip", "show", "-v", "boto3"]).decode("utf-8").split("\n")
	latest_version = [line.split(":")[1].strip() for line in latest_version if "Version" in line][0]
	if packaging.version.parse(current_version) < packaging.version.parse("1.26.50"):
		subprocess.run(["pip", "install", "--upgrade", "boto3"], check=True)
		print("boto3 package installed successfully")
	else:
		print("boto3 package version is already >= 1.26.50")
except subprocess.CalledProcessError as e:
	try:
		subprocess.run(["pip", "install", "--upgrade", "--proxy", UMG_PROXY, "boto3"], check=True)
		print("boto3 package installed successfully")
	except subprocess.CalledProcessError as e:
		print("Error: Failed to install boto3 package")
		print("Error code: ", e.returncode)
		print("Error message: ", e.output)

# Check if botocore >= 1.29.50, if not download latest version
try:
	current_version = subprocess.check_output(["pip", "show", "botocore"]).decode("utf-8").split("\n")
	current_version = [line.split(":")[1].strip() for line in current_version if "Version" in line][0]
	latest_version = subprocess.check_output(["pip", "show", "-v", "botocore"]).decode("utf-8").split("\n")
	latest_version = [line.split(":")[1].strip() for line in latest_version if "Version" in line][0]
	if packaging.version.parse(current_version) < packaging.version.parse("0.10.0"):
		subprocess.run(["pip", "install", "--upgrade", "botocore"], check=True)
		print("botocore package installed successfully")
	else:
		print("botocore package version is already >=1.29.50")
except subprocess.CalledProcessError as e:
	try:
		subprocess.run(["pip", "install", "--upgrade", "--proxy", UMG_PROXY, "botocore"], check=True)
		print("botocore package installed successfully")
	except subprocess.CalledProcessError as e:
		print("Error: Failed to install botocore package")
		print("Error code: ", e.returncode)
		print("Error message: ", e.output)

# Check if caosdb >= 0.10.0, if not download latest version
try:
	current_version = subprocess.check_output(["pip", "show", "caosdb"]).decode("utf-8").split("\n")
	current_version = [line.split(":")[1].strip() for line in current_version if "Version" in line][0]
	latest_version = subprocess.check_output(["pip", "show", "-v", "caosdb"]).decode("utf-8").split("\n")
	latest_version = [line.split(":")[1].strip() for line in latest_version if "Version" in line][0]
	if packaging.version.parse(current_version) < packaging.version.parse("0.10.0"):
		subprocess.run(["pip", "install", "--upgrade", "caosdb"], check=True)
		print("caosdb package installed successfully")
	else:
		print("caosdb package version is already >= 0.10.0")
except subprocess.CalledProcessError as e:
	try:
		subprocess.run(["pip", "install", "--upgrade", "--proxy", UMG_PROXY, "caosdb"], check=True)
		print("caosdb package installed successfully")
	except subprocess.CalledProcessError as e:
		print("Error: Failed to install caosdb package")
		print("Error code: ", e.returncode)
		print("Error message: ", e.output)

#############################################################################

os.system("echo ''")

#############################################################################

os.system("echo 'Starting streamlit now...'")

os.system("echo ''")

# run the Streamlit app with the --server.maxUploadSize flag
# 5000 = 5GB
subprocess.run(["streamlit", "run", app_path, "--server.maxUploadSize=5000"])

#############################################################################

# @echo off
# "C:\path\to\python.exe" "C:\path\to\myscript.py"
# pause
