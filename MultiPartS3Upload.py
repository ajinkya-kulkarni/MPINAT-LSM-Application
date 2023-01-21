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

###############################################################

import os
import logging
import boto3
from botocore.exceptions import ClientError

import sys
sys.dont_write_bytecode = True # Don't generate the __pycache__ folder locally
sys.tracebacklimit = 0 # Print exception without the buit-in python warning

# Initialize the logger
logger = logging.getLogger()
logger.setLevel(logging.ERROR)

# Create a boto3 client for S3, import data from the PASSWORDS.py file
from PASSWORDS import *

s3 = boto3.client('s3', endpoint_url = AMAZON_S3_ENDPOINT_URL, aws_access_key_id = AMAZON_S3_ACCESS_KEY, aws_secret_access_key = AMAZON_S3_SECRET_KEY)

def make_multipart_upload(tiff_file, bucket_name, amazon_bucket_target_name, FolderPathKey):
	try:
		# Create a multipart upload
		response = s3.create_multipart_upload(Bucket=bucket_name, Key=amazon_bucket_target_name)

		# Get the upload ID
		upload_id = response['UploadId']

		# Initialize the part number and the parts list
		part_number = 1
		parts = []

		try:
			# Get the size of the file
			file_size = os.path.getsize(os.path.join(FolderPathKey, tiff_file))
			part_size = 5 * 1024 * 1024

			# Iterate through the file and upload each part
			with open(os.path.join(FolderPathKey, tiff_file), 'rb') as f:
				for i in range(0, file_size, part_size):
					# Get the current part
					part = f.read(part_size)

					# Upload the part
					response = s3.upload_part(Body=part, Bucket=bucket_name, Key=amazon_bucket_target_name, PartNumber=part_number, UploadId=upload_id)

					# Append the part to the parts list
					parts.append({'ETag': response['ETag'], 'PartNumber': part_number})

					# Increment the part number
					part_number += 1

					# Print the upload progress
					print(f"Uploading {tiff_file}, {int(((i + part_size) / file_size) * 100)}% complete")

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
