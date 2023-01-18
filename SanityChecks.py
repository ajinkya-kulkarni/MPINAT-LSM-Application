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

# Function which ...

def SanityChecks(my_list1, my_list2, my_list3):

	counter = 0

	for i in range(len(my_list1)):

		if my_list1[i] == 'Yes':

			if (float(my_list2[i]) < 0 or my_list2[i] == '0' or float(my_list3[i]) < 0 or my_list3[i] == '0'):
				
				counter = counter + 1

		else:
			
			if (float(my_list2[i]) < 0 or my_list2[i] != '0' or float(my_list3[i]) < 0 or my_list3[i] != '0'):
				
				counter = counter + 1

	return counter