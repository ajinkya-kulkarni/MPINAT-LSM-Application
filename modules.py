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
import numpy as np

import datetime
import glob
import csv

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

########################################################################################

def make_LSM_overview(LINKAHEAD_URL, LINKAHEAD_USERNAME, LINKAHEAD_PASSWORD, UMG_PROXY):
	# Attempt to connect to the Linkahead database without using a proxy server
	try:
		db.configure_connection(
			url = LINKAHEAD_URL,
			password_method = "plain",
			ssl_insecure = True, # remove after naming server
			username = LINKAHEAD_USERNAME,
			password = LINKAHEAD_PASSWORD,
			timeout = 1000
		)

	# If connection fails, try again using a proxy server
	except:
		try:
			db.configure_connection(
				url = LINKAHEAD_URL,
				password_method = "plain",
				ssl_insecure = True, # remove after naming server
				username = LINKAHEAD_USERNAME,
				password = LINKAHEAD_PASSWORD,
				https_proxy = UMG_PROXY,
				timeout = 1000
			)

		# If connection still fails, raise an exception
		except:
			raise Exception('Unsuccessful connection with the Linkahead DB. Contact the admin(s) for help.')
			
	#######################################################################################

	### Extract all relevant entries from the Linkahead DB

	# Find all LSM scan entries in the database
	LSM_entries = db.execute_query('FIND RECORD LSM_SCAN')

	# Define file path pattern for output CSV files
	file_path_pattern = "LSM_overview_*.csv"

	# Remove all output CSV files that match the pattern
	for file_path in glob.glob(file_path_pattern):
		os.remove(file_path)

	# Get the current date and time in the format DD_Month_YYYY_HM_hrs
	now = datetime.datetime.now()
	timestamp = now.strftime("%d_%B_%Y_%H%M_hrs")

	# Construct the new filename with the timestamp
	filename = f"LSM_overview_{timestamp}.csv"
	
	try:
		# Loop over each LSM scan entry and extract relevant data
		for single_entry in LSM_entries:
			
			#######################################################################################

			# Extract sample information
			SampleID = np.array(single_entry.get_property_values('Sample'))[0]
			SampleName = np.array(db.execute_query(f"FIND SAMPLE WITH id = '{SampleID}'", 
												unique=True).get_property_values('name'))[0]
			
			#######################################################################################

			# Extract operator information
			OperatorID = np.array(single_entry.get_property_values('operator'))[0]
			GivenName = np.array(db.execute_query(f"FIND PERSON WITH id = '{OperatorID}'", 
												unique=True).get_property_values('given_name'))[0]
			FamilyName = np.array(db.execute_query(f"FIND PERSON WITH id = '{OperatorID}'", 
												unique=True).get_property_values('family_name'))[0]
			EmailAddress = np.array(db.execute_query(f"FIND PERSON WITH id = '{OperatorID}'", 
													unique=True).get_property_values('email_address'))[0]
			#######################################################################################

			# Extract LSM scan information
			Date = np.array(single_entry.get_property_values('date'))[0]
			DeltaPixelXY = np.array(single_entry.get_property_values('delta_pixel_xy'))[0]
			DeltaPixelZ = np.array(single_entry.get_property_values('delta_pixel_z'))[0]
			NumberOfChannels = np.array(single_entry.get_property_values('number_of_channels'))[0]
			
			#######################################################################################

			# Extract filter/wavelengths information
			n = len(np.array(single_entry.get_property_values('filters')).flatten())
			filter_names = {}
			for i, single_filter in enumerate(np.array(single_entry.get_property_values('filters')).flatten(), 1):
				name = np.array(db.execute_query(f"FIND Wavelengths WITH id = '{single_filter}'", 
												unique=True).get_property_values('name'))[0]
				filter_names[f"filter_{i}"] = name
			wavelengths_only = np.array(list(filter_names.values()))
			wavelengths_only = ', '.join([str(x) for x in wavelengths_only])
			
			#######################################################################################

			# Extract illumination information
			IlluminationLeft = np.array(single_entry.get_property_values('illumination_left'))[0]
			IlluminationRight = np.array(single_entry.get_property_values('illumination_right'))[0]
			
			#######################################################################################

			# Extract aperture information
			Apertures = np.array(single_entry.get_property_values('apertures')).flatten()
			Apertures = ', '.join([str(x) for x in Apertures])
			
			#######################################################################################

			# Extract exposure time information
			ExposureTimes = np.array(single_entry.get_property_values('exposure_times')).flatten()
			ExposureTimes = ', '.join([str(x) for x in ExposureTimes])
			
			#######################################################################################

			# Extract objective, zoom, sheet width and additional comments information
			Objective = np.array(single_entry.get_property_values('objective'))[0]
			Zoom = np.array(single_entry.get_property_values('zoom'))[0]
			SheetWidth = np.array(single_entry.get_property_values('sheet_width'))[0]
			AdditionalComments = np.array(single_entry.get_property_values('additional_comments'))[0]
			
			#######################################################################################

			# Combine all extracted information into an array
			results_array = np.array([SampleName, GivenName, FamilyName, EmailAddress, Date, 
									DeltaPixelXY, DeltaPixelZ, NumberOfChannels, wavelengths_only,
									IlluminationLeft, IlluminationRight, Apertures, ExposureTimes, 
									Objective, Zoom, SheetWidth, AdditionalComments], dtype = object)

			# Replace empty strings with 'None' if any field is left empty originally
			results_array = ['None' if x == '' else x for x in results_array]
			
			#######################################################################################

			# Write array to CSV file
			with open(filename, mode='a', newline='') as file:

				# Create CSV writer
				writer = csv.writer(file)

				# If the file is empty, write the header row
				if file.tell() == 0:
					writer.writerow(['Sample ID/Barcode', 'Operator given name', 'Operator family name', 
									'Operator email address', 'Upload date', 'Delta pixel XY', 'Delta pixel Z', 
									'Number of Channels', 'Wavelengths', 'Illumination Left', 'Illumination Right', 
									'Apertures', 'Exposure times', 'Objective', 'Zoom', 
									'Sheet width', 'Additional comments'])

				# Write the current data row to the CSV file
				writer.writerow(results_array)

		#######################################################################################

		# Print success message
		print("LSM_overview.csv created successfully")

	except:
		# If an error occurs, raise an exception
		raise Exception('Something went wrong')
	
#######################################################################################