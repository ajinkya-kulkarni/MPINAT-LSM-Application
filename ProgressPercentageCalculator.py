
import sys
sys.dont_write_bytecode = True # Don't generate the __pycache__ folder locally

import threading
import time

#######################################################################

# Functions to get size of file transferred to S3 buckets.

# Taken from https://stackoverflow.com/questions/55799556/make-boto3-upload-calls-blocking-single-threaded

def get_bufsize(buf, chunk = 1024) -> int:
	start = buf.tell()
	try:
		size = 0 
		while True: 
			out = buf.read(chunk) 
			if out: 
				size += chunk 
			else: 
				break
		return size
	finally:
		buf.seek(start)

class ProgressPercentage(object):

	def __init__(self, filename, buf):
		self._filename = filename
		self._size = float(get_bufsize(buf))
		self._seen_so_far = 0
		self._lock = threading.Lock()
		self.start = None

	def __call__(self, bytes_amount):
		with self._lock:
			if not self.start:
				self.start = time.monotonic()
			self._seen_so_far += bytes_amount
			percentage = (self._seen_so_far / self._size) * 100

			sys.stdout.write("\r %s currently %.2f%% done \n" % (self._filename, percentage))

			sys.stdout.flush()