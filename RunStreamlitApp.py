import os
import urllib.request
import subprocess

# get the current directory path
directory_path = os.getcwd()

# specify the file name
file_name = "LSM_StreamlitApp.py"

# specify the url of the file you want to download
url = "https://raw.githubusercontent.com/ajinkya-kulkarni/MPINAT-LSM-Application/main/LSM_StreamlitApp.py"

# download the file and save it to a local file
try:
    urllib.request.urlretrieve(url, file_name)
    print(f"{file_name} downloaded successfully")
except urllib.error.HTTPError as e:
    print(f"Error: {e.code}")
except urllib.error.URLError as e:
    print(f"Error: {e.reason}")

# specify the path to the Streamlit app
app_path = os.path.join(directory_path, file_name)

# run the Streamlit app with the --server.maxUploadSize flag
# 5000 = 5GB
result = subprocess.run(["streamlit", "run", app_path, "--server.maxUploadSize=5000"])

if result.returncode != 0:
    print("An error occurred while running the Streamlit app.")