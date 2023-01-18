
import os
import urllib.request
import subprocess

#############################################################################

os.system('cls||clear')

print()

#############################################################################

# Define the proxy server

UMG_PROXY = 'http://anonymous@astaro01-proxy.med.uni-goettingen.de:8080'

#############################################################################

# Remove existing files if they exist

def check_and_delete(file_name):
    file_path = os.path.join(os.getcwd(), file_name)

    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Deleted old {file_name}")

file_names = ["MainRunner.py"]

for file_name in file_names:
    check_and_delete(file_name)

check_and_delete("ErrorLogs.txt")

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

# Run MainRunner.py

script_file_name = "MainRunner.py"

# specify the path to the Streamlit app
script_path = os.path.join(os.getcwd(), script_file_name)

os.system("echo 'Starting MainRunner now...'")

#############################################################################

print()

#############################################################################

subprocess.run(["python", script_path])

#############################################################################