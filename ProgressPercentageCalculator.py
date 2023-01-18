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

import sys
sys.dont_write_bytecode = True # Don't generate the __pycache__ folder locally

import os
import threading

# Functions to get size of file transferred to S3 buckets.

class ProgressPercentage(object):

	def __init__(self, filename):

		self._filename = filename
		self._size = float(os.path.getsize(filename))
		self._seen_so_far = 0
		self._lock = threading.Lock()

	def __call__(self, bytes_amount):

		with self._lock:

			self._seen_so_far = self._seen_so_far + bytes_amount

			percentage = (self._seen_so_far / self._size) * 100

			sys.stdout.write("\r%s  %s / %s  (%.1f%%)" % (self._filename, self._seen_so_far, self._size, percentage))

			sys.stdout.flush()