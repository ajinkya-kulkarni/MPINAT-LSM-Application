[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

# LSM Scan Uploader

This is a repository for accessing the source codes for the datalake and Linkahead interfaces used in the ABA project at the Max Planck Institute for Multidisciplinary Sciences, Göttingen. This is a Python script that can be used to upload LSM scan images and metadata to an Amazon S3 bucket and a CaosDB server, respectively. It is designed to work with light sheet microscopy files.

## Prerequisites

- Python 3.6 or higher
- `pip` package manager
- `os`, `urllib`, `subprocess`, `json`, `datetime`, `streamlit`, `caosdb`, `time`, `logging`, `threading`, `io`, `urllib3`, `boto3`, `botocorepackages` 

Use `pip install package_name` to install all these packages)

## How to Use

1. Open the terminal or command prompt.
2. Clone or download the repository and navigate to the project directory.
3. Run `python MainProgram.py`.
4. Enter the required information when prompted (sample ID/barcode, image and metadata paths, etc.).
5. Wait for the program to finish uploading the images and metadata.

## Credits
This web application was developed, tested, and maintained by Ajinkya Kulkarni at the Max Planck Institute for Multidisciplinary Sciences, Göttingen.

## License
This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Contact
For more information or to provide feedback, please visit the project repository or contact the developer directly.
