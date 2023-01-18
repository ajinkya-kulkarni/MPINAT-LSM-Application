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

import subprocess
import packaging.version

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
