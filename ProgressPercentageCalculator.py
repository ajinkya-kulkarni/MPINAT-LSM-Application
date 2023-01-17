
import sys
sys.dont_write_bytecode = True # Don't generate the __pycache__ folder locally

import os
import threading

#######################################################################

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