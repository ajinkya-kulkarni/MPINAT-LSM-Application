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

# Function which checks for erroneous input(s) for Aperture(s), Exposure Time(s) and Active Channels and returns the appropriate exception

def SanityChecks(my_list1, my_list2, my_list3):
	for i in range(len(my_list1)):
		is_active = my_list1[i] == 'Yes'
		aperture = int(my_list2[i])
		exposure_time = int(my_list3[i])
		if is_active:
			if aperture == 0:
				raise ValueError("Aperture(s) should not be 0 for active channels")
			if exposure_time == 0:
				raise ValueError("Exposure Time(s) should not be 0 for active channels")
		else:
			if aperture != 0:
				raise ValueError("Aperture(s) should be 0 for non-active channels")
			if exposure_time != 0:
				raise ValueError("Exposure Time(s) should be 0 for non-active channels")