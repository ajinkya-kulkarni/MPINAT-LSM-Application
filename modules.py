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
from botocore.exceptions import ClientError

from datetime import datetime
import urllib.request
import json

import caosdb as db
import urllib3
urllib3.disable_warnings() # Disable the HTTPS warnings for CaosDB authentication

import sys
# Don't generate the __pycache__ folder locally
sys.dont_write_bytecode = True 
# Print exception without the buit-in python warning
sys.tracebacklimit = 0 

# Initialize the logger
import logging
logger = logging.getLogger()
logger.setLevel(logging.ERROR)

########################################################################################

from PASSWORDS import *

########################################################################################

# Create a boto3 client for S3, import data from the PASSWORDS.py file

s3 = boto3.client('s3', endpoint_url = AMAZON_S3_ENDPOINT_URL, aws_access_key_id = AMAZON_S3_ACCESS_KEY, aws_secret_access_key = AMAZON_S3_SECRET_KEY)

def make_multipart_upload(tiff_file, bucket_name, amazon_bucket_target_name, FolderPathKey):

	"""
	This function creates a multipart upload in the specified S3 bucket and uploads the specified tiff file to the specified target name in the bucket.

	Parameters:
		tiff_file (str): The name of the tiff file to be uploaded.
		bucket_name (str): The name of the S3 bucket where the file will be uploaded.
		amazon_bucket_target_name (str): The target name for the file in the S3 bucket.
		FolderPathKey (str): The path to the folder where the tiff file is located.
		
	Returns:
		None
	"""

	try:
		# Create a multipart upload
		response = s3.create_multipart_upload(Bucket=bucket_name, Key=amazon_bucket_target_name)

		# Get the upload ID
		upload_id = response['UploadId']

		# Initialize the part number and the parts list
		part_number = 1
		parts = []
		
		try:
			# Upload the part
			response = s3.upload_part(Body=open(os.path.join(FolderPathKey, tiff_file), 'rb'), Bucket=bucket_name, Key=amazon_bucket_target_name, PartNumber=part_number, UploadId=upload_id)

			# Append the part to the parts list
			parts.append({'ETag': response['ETag'], 'PartNumber': part_number})

			# Increment the part number
			part_number += 1

		except ClientError as e:

			logger.error("Failed to upload %s", tiff_file, exc_info=True)
			pass
		try:
			# Complete the multipart upload
			response = s3.complete_multipart_upload(Bucket=bucket_name, Key=amazon_bucket_target_name, UploadId=upload_id, MultipartUpload={'Parts': parts})
		except ClientError as e:
			logger.error("Failed to complete multipart upload", exc_info=True)
			pass
	finally:
		s3.close()

########################################################################################

# Function which checks for erroneous input(s) for Aperture(s), Exposure Time(s) and Active Channels and returns the appropriate exception

def SanityChecks(my_list1, my_list2, my_list3):
	"""
	This function performs sanity checks on the provided lists.
	Parameters:
		my_list1 (list): A list of strings representing whether a channel is active or not. The string should be 'Yes' or 'No'.
		my_list2 (list): A list of integers representing the aperture of the corresponding channel in my_list1.
		my_list3 (list): A list of integers representing the exposure time of the corresponding channel in my_list1.
	Returns:
		None
	Raises:
		ValueError: If aperture or exposure time is not as expected for the corresponding active/non-active channel.
	"""
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

#######################################################################################

def check_last_commit(mode=None):
	"""
	Checks the last commit time of the MPINAT-LSM-Application GitHub repository owned by ajinkya-kulkarni.

	Args:
		mode (str, optional): If set to 'Test', the function will print the elapsed time instead of raising an exception. Defaults to None.

	Raises:
		Exception: If the elapsed time since the last commit is less than 500 seconds, and mode is not set to 'Test', an exception will be raised with a message indicating that the application has been recently updated by the admin(s) and the user should wait for 10 more minutes before trying again.
	"""

	repo_name = "MPINAT-LSM-Application"
	repo_owner = "ajinkya-kulkarni"

	try:
		# send an HTTP GET request to the GitHub API to retrieve information about the latest push
		url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
		request = urllib.request.Request(url)
		request.add_header('User-Agent', 'Mozilla/5.0')
		response = urllib.request.urlopen(request)
		data = json.loads(response.read())
		last_commit_time = data['pushed_at']
	except:
		try:
			# try again without a proxy
			response = urllib.request.urlopen(url)
			data = json.loads(response.read())
			last_commit_time = data['pushed_at']
		except:
			raise Exception('Failed to fetch information about the latest GitHub push.')

	# parse the timestamp to a datetime object
	last_commit_datetime = datetime.strptime(last_commit_time, "%Y-%m-%dT%H:%M:%SZ")
	# get the current time
	now = datetime.utcnow()
	# calculate the time elapsed
	elapsed = now - last_commit_datetime

	if mode == 'Test':
		# If the mode is set to 'test', print the elapsed time instead of raising an exception.
		print(f"Last commit was made {int(elapsed.total_seconds())} seconds ago.")
	elif elapsed.total_seconds() < 500:
		# If the elapsed time is less than 500 seconds, raise an exception with a message indicating that
		# the application has been recently updated by the admin(s) and the user should wait for 10 more minutes before trying again.
		raise Exception(f"Application has been recently updated by the Admin(s). Please wait for 10 more minutes and try again.")

#######################################################################################
