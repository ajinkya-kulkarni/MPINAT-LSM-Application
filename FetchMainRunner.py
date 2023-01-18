import os
import urllib.request
import subprocess

def check_and_delete(file_names: List[str]):
    """
    Deletes a list of files if they exist in the current working directory
    """
    for file_name in file_names:
        file_path = os.path.join(os.getcwd(), file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted old {file_name}")

def download_file(url: str, proxy: str=None):
    """
    Download a file from the specified URL.
    :param url: The URL of the file to download.
    :param proxy: (optional) The proxy to use for the download.
    """
    file_name = url.split("/")[-1]
    try:
        urllib.request.urlretrieve(url, file_name)
        print(f"Latest {file_name} fetched successfully")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} {e.reason}")
        if proxy:
            try:
                proxy_support = urllib.request.ProxyHandler({'http': proxy})
                opener = urllib.request.build_opener(proxy_support)
                urllib.request.install_opener(opener)
                urllib.request.urlretrieve(url, file_name)
                print(f"Latest {file_name} fetched successfully")
            except:
                urllib.request.install_opener(None)
                print("Failed to fetch the file with proxy")
        else:
            print("Failed to fetch the file without proxy")

def run_script(script_file_name: str):
    """
    Runs a python script using subprocess
    """
    script_path = os.path.join(os.getcwd(), script_file_name)
    subprocess.run(["python", script_path])

#######################################################################

# Run the program

os.system('cls||clear')

UMG_PROXY = 'http://anonymous@astaro01-proxy.med.uni-goettingen.de:8080'

check_and_delete("ErrorLogs.txt")

file_names = ["MainRunner.py"]

check_and_delete(file_names)

base_url = "https://raw.githubusercontent.com/ajinkya-kulkarni/MPINAT-LSM-Application/main/"
for file_name in file_names:
    url = f"{base_url}{file_name}"
    download_file(url, UMG_PROXY)

os.system("echo 'Starting MainRunner now...'")

run_script("MainRunner.py")

#######################################################################