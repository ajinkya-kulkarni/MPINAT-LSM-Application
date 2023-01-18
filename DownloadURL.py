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

import urllib

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