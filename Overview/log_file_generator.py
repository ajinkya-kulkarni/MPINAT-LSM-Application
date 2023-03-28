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
#
# Visit https://docs.indiscale.com/ for CaosDB Documentation.

# UX/UI recommendations provided by Radhika Bhagwat (radhika.bhagwat3@gmail.com, Product Designer) and Md Motiur Rahman Sagar <motiur.sagar@mpinat.mpg.de>

########################################################################################

import os

import boto3
import caosdb as db

from datetime import datetime

import urllib3
urllib3.disable_warnings() # Disable the HTTPS warnings for CaosDB authentication

import sys
sys.dont_write_bytecode = True # Don't generate the __pycache__ folder locally
sys.tracebacklimit = 0 # Print exception without the buit-in python warning

########################################################################################

from ..PASSWORDS import *

####################################################################################

def make_log_file():
	"""
	Creates a log file with a list of files in an Amazon S3 bucket and deletes all files containing 'TestSample_0' in their key name. This function retrieves a list of all objects in the specified Amazon S3 bucket and writes their names and upload dates to a text file named 'S3_files.txt' in the current working directory. It then loops over all objects in the bucket that contain the word 'TestSample_0' in their key name and deletes them.

	Parameters:
		None

	Returns:
		None

	Raises:
		Exception: If an error occurs during the deletion process.
	"""

	print()

	# Create an S3 resource object using endpoint URL and access keys
	s3 = boto3.resource('s3',endpoint_url=AMAZON_S3_ENDPOINT_URL, aws_access_key_id=AMAZON_S3_ACCESS_KEY, aws_secret_access_key=AMAZON_S3_SECRET_KEY)

	########################################################################

	# Create a Bucket object representing the specified Amazon S3 bucket
	bucket = s3.Bucket(AMAZON_S3_BUCKET)

	# Get list of objects in the bucket
	objects = list(bucket.objects.all())

	# Get total number of files in the bucket
	total_files = len(objects)

	print(str(total_files) + " files/entries retreived successfully")
	print()

	########################################################################

	filename = 'S3_files.txt'

	if os.path.exists(filename):
		os.remove(filename)

	########################################################################

	with open('S3_files.txt', 'w') as file:
		# Write the first line with timestamp
		timestamp = datetime.now().strftime('%d %B %Y at %H:%M hrs')
		file.write('Log generated on ' + timestamp + '\n')
		file.write('\n')
		
		# Loop over each object in the bucket and write its name and upload date to the text file
		for i in range(total_files):

			obj = objects[i]

			# Write object name and upload date to text file
			file.write(obj.key + ' ' + obj.last_modified.strftime('(Created on : ' + '%d %B %Y at %H:%M hrs)') + '\n')

	########################################################################

	# Loop over all objects in the bucket that contain the word 'TestSample_0' in their key name

	for i in range(total_files):
		obj = objects[i]

		if ('TestSample_0' in obj.key):
			try:
				print(str(obj.key) + ' found')
				# Delete the object
				obj.delete()
				# Print message indicating that the object was deleted successfully
				print(str(obj.key) + ' deleted')
				print()
			except:
				# If an error occurs, raise an exception
				raise Exception('Something went wrong')

####################################################################################

if __name__ == '__main__':

	os.system('clear || cls')

	make_log_file()

####################################################################################