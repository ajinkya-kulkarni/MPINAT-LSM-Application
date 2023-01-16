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

# UX/UI recommendations provided by Radhika Bhagwat (radhika.bhagwat3@gmail.com, Product Designer)

###############################################################

# Run this script as streamlit run LSM_StreamlitApp.py --server.maxUploadSize 5000 # Max size of each uploaded file is 5000mb

###############################################################

# TODO: 
# 1. Add a progress bar for the S3 uploads based on the progress callback.

###############################################################

import streamlit as st

import caosdb as db

from datetime import date
import time

import os
import logging

import sys
sys.dont_write_bytecode = True # Don't generate the __pycache__ folder locally

import threading

import boto3
from botocore.exceptions import ClientError

from PASSWORDS import *

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

#######################################################################

# Some initial config info regarding the web app

st.set_page_config(page_title = 'LSM Application', page_icon = None, layout = "wide", initial_sidebar_state = "expanded", menu_items = {'Get help': 'mailto:ajinkya.kulkarni@mpinat.mpg.de', 'Report a bug': 'mailto:ajinkya.kulkarni@mpinat.mpg.de', 'About': 'This is a webpage for uploading the LSM images and the metadata used in the ABA project at the MPI-NAT, Goettingen. Developed, tested and maintained by Ajinkya Kulkarni: https://github.com/ajinkya-kulkarni and reachable at mailto:ajinkya.kulkarni@mpinat.mpg.de'
})

# Title of the web app

st.title(':blue[Application for uploading LSM images and metadata]')

#######################################################################

# Initialize the form

with st.form(key = 'LSM_SCAN_FORM_KEY', clear_on_submit = True):

	# Establish connection with the CaosDB server

	try:

		db.configure_connection(
		url = LINKAHEAD_URL,
		password_method = "plain",
		ssl_insecure = True, # remove after naming server
		username = LINKAHEAD_USERNAME,
		password = LINKAHEAD_PASSWORD,
		timeout = 1000
		)

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

		except:
			
			ErrorMessage = st.error('Unsuccessful connection with the Linkahead DB. Contact the admin(s) for help.', icon = None)

			st.stop()

	###############################################################

	# Information regarding the Amazon S3 bucket

	access_key = AMAZON_S3_ACCESS_KEY

	secret_key = AMAZON_S3_SECRET_KEY

	bucket_name = AMAZON_S3_BUCKET

	gwdg_client = boto3.client('s3', endpoint_url = AMAZON_S3_ENDPOINT_URL, aws_access_key_id = access_key, aws_secret_access_key = secret_key)

	gwdg = boto3.resource('s3', endpoint_url = AMAZON_S3_ENDPOINT_URL, aws_access_key_id = access_key, aws_secret_access_key = secret_key)

	###############################################################

	# Get the information about users and LSM_SCAN from the CaosDB server.

	persons = db.execute_query("FIND RECORD Person")
	FamilyNames = []
	GivenNames = []
	NameIDs = []
	ComboNames = []
	for person in persons:
		FamilyNames.append(person.get_property("family_name").value)
		GivenNames.append(person.get_property("given_name").value)
		NameIDs.append(person.id)

		ComboNames += ([str(person.get_property("family_name").value) + str(', ') + str(person.get_property("given_name").value)])

	wavelengths = db.execute_query("FIND RECORD Wavelengths")
	ChannelIDs = []
	ChannelNames = []
	for single_wavelength in wavelengths:
		ChannelIDs.append(single_wavelength.id)
		ChannelNames.append(single_wavelength.get_property_values("name")[0])

	###############################################################

	st.subheader(':blue[Preliminary details]')

	st.selectbox('Select the person', ComboNames, label_visibility = "visible", key = '-PersonKey-')

	st.text_input('Sample ID or Barcode (*mandatory)', 
	'TestSample_0', key = '-SampleIDKey-')

	# Date selection widget

	st.date_input("Date of uploading the LSM image(s)", date.today(), key = '-DateKey-')

	st.markdown("""---""")

	# Upload widget

	st.subheader(':blue[Select the files to be uploaded]')

	UploadedFiles = st.file_uploader("Select the folder containing the images (only tiff or tif files)", type = ['tif', 'tiff'], label_visibility = "collapsed", accept_multiple_files = True)

	###############################################################

	st.markdown("""---""")

	###############################################################

	st.subheader(':blue[Fill in information regarding the channels]')

	st.caption('Number of channels should be more than 0 and equal to the number of "Yes" for the active channels', unsafe_allow_html = False)

	st.markdown("")

	st.text_input('Number of channels', key = '-NumberChannelsKey-', value = '0', placeholder = '0')

	st.markdown("")

	left_column1, middle_column1, right_column1  = st.columns(3)

	with left_column1:
		
		for i in range(1, len(ChannelNames) + 1):
			
			st.selectbox('Channel: ' + f'{ChannelNames[i-1]}', ('No', 'Yes'), key = f'-Channel{i}Key-')

	with middle_column1:

		for i in range(1, len(ChannelNames) + 1):
			
			st.text_input(f'Aperture', value='0', placeholder='0', key = f'-Aperture{i}Key-')

	with right_column1:

		for i in range(1, len(ChannelNames) + 1):
			
			st.text_input(f'Exposure Time (micro s)', value='0', placeholder='0', key = f'-ExposureTime{i}Key-')

	st.markdown("""---""")

	###############################################################

	st.subheader(':blue[Select illumination information]')

	st.caption('selecting at least one is mandatory', unsafe_allow_html = False)

	st.markdown("")

	left_column2, right_column2  = st.columns(2)

	with left_column2:

		st.checkbox('Illumination Left', value = False, key = '-IlluminationLeftKey-', label_visibility = 'visible')

	with right_column2:

		st.checkbox('Illumination Right', value = False, key = '-IlluminationRightKey-', label_visibility = 'visible')

	st.markdown("""---""")

	st.subheader(':blue[Fill in the resolution information]')

	left_column3, right_column3  = st.columns(2)

	with left_column3:

		st.text_input('Resolution in XY Plane (*mandatory, micro m)', value = '0', placeholder = '0', key = '-ResolutionInXYPlaneKey-')

	with right_column3:

		st.text_input('Resolution in Z direction (*mandatory, micro m)', value = '0', placeholder = '0', key = '-ResolutionZDirectionKey-')

	st.markdown("""---""")

	###############################################################

	st.subheader(':blue[Additional Comments]')

	st.text_area('Additional Comments', placeholder = 'None', label_visibility = 'collapsed', key = '-AdditionalCommentsKey-')

	###############################################################

	# Submit the form

	submitted = st.form_submit_button('Submit')

	###############################################################

	if (submitted and len(UploadedFiles) > 0):

		SampleKey = st.session_state['-SampleIDKey-']
		if SampleKey is None:
			st.error('Sample ID or Barcode should not be empty', icon = None)
			st.stop()

		####################

		All_Channel_Keys = []
		for i in range(1, len(ChannelNames) + 1):
			All_Channel_Keys.append(st.session_state[f'-Channel{i}Key-'])

		Active_Channels = All_Channel_Keys.count('Yes')
		if (int(Active_Channels) == 0):
			st.error('Select at least 1 active channel', icon = None)
			st.stop()

		####################

		NumberChannelsKey = st.session_state['-NumberChannelsKey-']
		try:
			type(int(NumberChannelsKey))
		except:
			st.error('Channel number should be an integer', icon = None)
			st.stop()
		
		if (int(NumberChannelsKey) != int(Active_Channels)):
			st.error('Number of channels should be equal to the number of "Yes" for the active channels', icon = None)
			st.stop()

		if (int(NumberChannelsKey) == 0):
			st.error('Number of channels should be more than 0', icon = None)
			st.stop()

		####################

		ResolutionInXYPlaneKey = st.session_state['-ResolutionInXYPlaneKey-']
		try:
			type(float(ResolutionInXYPlaneKey))
		except:
			st.error('Resolution in XY Plane should be a number', icon = None)
			st.stop()

		if (float(ResolutionInXYPlaneKey) <= 0):
			st.error('Resolution in XY Plane should be more than 0', icon = None)
			st.stop()

		####################

		ResolutionZDirectionKey = st.session_state['-ResolutionZDirectionKey-']
		try:
			type(float(ResolutionZDirectionKey))
		except:
			st.error('Resolution in Z direction should be a number', icon = None)
			st.stop()

		if (float(ResolutionZDirectionKey) <= 0):
			st.error('Resolution in Z direction should be more than 0', icon = None)
			st.stop()

		####################

		IlluminationLeftKey = st.session_state['-IlluminationLeftKey-']
		IlluminationRightKey = st.session_state['-IlluminationRightKey-']

		if (IlluminationLeftKey == False or IlluminationRightKey == False):
			st.error('Select at least one option for the illuminations', icon = None)
			st.stop()

		###############################################################

		# Start executing the form

		PersonKey = st.session_state['-PersonKey-']
		DateKey = st.session_state['-DateKey-']

		All_Aperture_Keys = []
		for i in range(1, len(ChannelNames) + 1):
			All_Aperture_Keys.append(st.session_state[f'-Aperture{i}Key-'])

		All_ExposureTime_Keys = []
		for i in range(1, len(ChannelNames) + 1):
			All_ExposureTime_Keys.append(st.session_state[f'-ExposureTime{i}Key-'])

		AdditionalCommentsKey = st.session_state['-AdditionalCommentsKey-']

		#######################################################

		result = zip(ComboNames, NameIDs)

		filtered = [(a, b) for a, b in zip(ComboNames, NameIDs) if a == PersonKey]

		NamePicked, NameIDPicked = zip(*filtered)

		filtered = []

		filtered = [(a, b, c, d, e) for a, b, c, d, e in zip(ChannelNames, ChannelIDs, All_Channel_Keys, All_Aperture_Keys, All_ExposureTime_Keys) if c == 'Yes']

		ChannelNamesPicked, ChannelIDsPicked, ChannelsPicked, AperturesPicked, ExposureTimesPicked = zip(*filtered)

		#######################################################

		try:

			sample_rec = db.execute_query(f"FIND RECORD Sample WITH sample_id = '{SampleKey}'", unique = True)

		except:

			ErrorMessage = st.error('Error with finding the requested specimen in the Linkahead DB! Please contact the admin(s) for help.', icon = None)

			st.stop()

		# Add metadata to the CaosDB server

		rec = db.Record().add_parent(name = "LSM_Scan")

		rec.add_property(name = "Sample", value = sample_rec)
		rec.add_parent(name = "LSM_Scan")

		rec.add_property(name = "operator", value = NameIDPicked[0])
		rec.add_property(name = "date", value = DateKey)

		rec.add_property(name = "delta_pixel_xy", value = ResolutionInXYPlaneKey)
		rec.add_property(name = "delta_pixel_z", value = ResolutionZDirectionKey)

		rec.add_property(name = "number_of_channels", value = NumberChannelsKey)
		rec.add_property(name = "filters", value = list(ChannelIDsPicked))

		rec.add_property(name = "illumination_left", value = IlluminationLeftKey)
		rec.add_property(name = "illumination_right", value = IlluminationRightKey)

		rec.add_property(name = "apertures", value = list(AperturesPicked))
		rec.add_property(name = "exposure_times", value = list(ExposureTimesPicked))

		rec.add_property(name = "additional_comments", value = AdditionalCommentsKey)

		#######################################################

		# Insert records to the CaosDB server

		try:

			rec.insert()

			SuccessMessageMetadata = st.success('Successfully uploaded metadata, please wait while the images are uploaded.')

		except:
			
			ErrorMessage = st.error('Error with inserting records in the Linkahead DB. Please contact the admin(s) for help.', icon = None)
			
			st.stop()

		#######################################################

		# Upload images to Amazon S3 bucket

		with st.spinner('Uploading the images now. Please wait.'):

			for SingleUploadedFile in UploadedFiles:

				amazon_bucket_target_name = SampleKey + '/' + str(SingleUploadedFile.name)

				try:

					# response = gwdg_client.upload_fileobj(SingleUploadedFile, bucket_name, amazon_bucket_target_name, Callback = ProgressPercentage(SingleUploadedFile.name, SingleUploadedFile))

					response = gwdg_client.upload_fileobj(SingleUploadedFile, bucket_name, amazon_bucket_target_name)

				except ClientError as e:

					ErrorMessage = st.error('Error with uploading images to the Amazon S3 bucket. Please contact the admin(s) for help.', icon = None)

					logging.error(e)

					st.stop()

				#######################################################

		uploaded_files_to_S3 = [file.key for file in gwdg.Bucket(bucket_name).objects.filter(Prefix = SampleKey)]

		#######################################################

		SuccessMessageImagesUpload = st.success('Successfully uploaded metadata and images. Refresh page to start a new upload.')

		st.stop()

#######################################################################