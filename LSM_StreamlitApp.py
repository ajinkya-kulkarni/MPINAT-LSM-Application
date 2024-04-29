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

import streamlit as st

from datetime import datetime
import time
import os
import logging
from io import BytesIO

import json

import sys
sys.dont_write_bytecode = True # Don't generate the __pycache__ folder locally
sys.tracebacklimit = 0 # Print exception without the buit-in python warning

import urllib3
urllib3.disable_warnings() # Disable the HTTPS warnings for CaosDB authentication
import caosdb as db

import boto3
from botocore.exceptions import ClientError

#######################################################################

from PASSWORDS import *
from modules import *

type_of_scan = 'LSM'

#######################################################################

SleepTime = 5

# Some initial config info regarding the web app

with open("logo.jpg", "rb") as f:
	image_data = f.read()

image_bytes = BytesIO(image_data)

st.set_page_config(page_title = 'LSM Application', page_icon = image_bytes, layout = "centered", initial_sidebar_state = "expanded", menu_items = {'Get help': 'mailto:ajinkya.kulkarni@mpinat.mpg.de', 'Report a bug': 'mailto:ajinkya.kulkarni@mpinat.mpg.de', 'About': 'This is a webpage for uploading the LSM images and the metadata used in the ABA project at the MPI-NAT, Göttingen. Developed, tested and maintained by Ajinkya Kulkarni: https://github.com/ajinkya-kulkarni and reachable at mailto:ajinkya.kulkarni@mpinat.mpg.de'
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
			time.sleep(SleepTime)
			ErrorMessage.empty()
			st.stop()

	###############################################################

	st.error('Unsuccessful connection with the Linkahead DB. Contact the admin(s) for help.', icon = None)
	st.stop()

	###############################################################

	# Information regarding the Amazon S3 bucket

	access_key = AMAZON_S3_ACCESS_KEY
	secret_key = AMAZON_S3_SECRET_KEY
	bucket_name = AMAZON_S3_BUCKET

	###############################################################

	# Get the information about users and LSM_SCAN from the CaosDB server.

	try:
		persons = db.execute_query("FIND RECORD Person")
	except:
		ErrorMessage = st.error('Unable to fetch persons record(s) in the Linkahead DB. Contact the admin(s) for help.', icon = None)
		time.sleep(SleepTime)
		ErrorMessage.empty()
		st.stop()
	
	FamilyNames = []
	GivenNames = []
	NameIDs = []
	ComboNames = []
	for person in persons:
		FamilyNames.append(person.get_property("family_name").value)
		GivenNames.append(person.get_property("given_name").value)
		NameIDs.append(person.id)

		ComboNames += ([str(person.get_property("family_name").value) + str(', ') + str(person.get_property("given_name").value)])

	try:
		wavelengths = db.execute_query("FIND RECORD Wavelengths")
	except:
		ErrorMessage = st.error('Unable to fetch wavelengths record(s) in the Linkahead DB. Contact the admin(s) for help.', icon = None)
		time.sleep(SleepTime)
		ErrorMessage.empty()
		st.stop()

	ChannelIDs = []
	ChannelNames = []
	for single_wavelength in wavelengths:
		ChannelIDs.append(single_wavelength.id)
		ChannelNames.append(single_wavelength.get_property_values("name")[0])

	###############################################################

	st.subheader(':blue[Preliminary details]')

	st.selectbox('Select the person', ComboNames, label_visibility = "visible", key = '-PersonKey-')

	st.text_input('Sample ID or Barcode', key = '-SampleIDKey-')

	# Test Sample ID = TestSample_0

	# Date selection widget

	st.date_input("Date when the LSM image(s) were scanned", datetime.today().date(), key = '-DateKey-')

	st.text_input('Write the path of the folder containing the images', value = "", key = '-FolderPathKey-')

	st.caption('Only tif or tiff images allowed', unsafe_allow_html = False)

	###############################################################

	st.markdown("""---""")

	###############################################################

	st.subheader(':blue[Fill in information regarding the channels]')

	st.caption('Number of channels should be more than 0 and equal to the number of active channels.', unsafe_allow_html = False)

	st.caption('Aperture(s) and Exposure Time(s) must be filled for active channels.', unsafe_allow_html = False)

	st.markdown("")

	st.number_input('Number of channels', key = '-NumberChannelsKey-', min_value = 0, max_value = len(ChannelNames), value = 0, step = 1, format = '%d')

	st.markdown("")

	left_column1, middle_column1, right_column1  = st.columns(3)

	with left_column1:
		
		for i in range(1, len(ChannelNames) + 1):
			
			st.selectbox('Channel: ' + f'{ChannelNames[i-1]}', ('No', 'Yes'), key = f'-Channel{i}Key-')

	with middle_column1:

		for i in range(1, len(ChannelNames) + 1):

			st.number_input(f'Aperture (%)', key = f'-Aperture{i}Key-', min_value = 0, max_value = 100, value = 0, step = 1, format = '%d')

	with right_column1:

		for i in range(1, len(ChannelNames) + 1):

			st.number_input(f'Exposure Time (micro s)', key = f'-ExposureTime{i}Key-', min_value = 0, value = 0, step = 1, format = '%d')

	st.markdown("""---""")

	###############################################################

	st.subheader(':blue[Select illumination information]')

	st.caption('Selecting at least one is mandatory', unsafe_allow_html = False)

	st.markdown("")

	left_column2, right_column2  = st.columns(2)

	with left_column2:

		st.checkbox('Illumination Left', value = False, key = '-IlluminationLeftKey-', label_visibility = 'visible')

	with right_column2:

		st.checkbox('Illumination Right', value = False, key = '-IlluminationRightKey-', label_visibility = 'visible')

	st.markdown("""---""")

	###############################################################

	st.subheader(':blue[Fill in the resolution information]')

	left_column3, right_column3  = st.columns(2)

	with left_column3:

		st.number_input('Resolution in XY Plane (micro m)', key = '-ResolutionInXYPlaneKey-', min_value = 0.0, value = 0.0, step = 0.1, format = '%0.1f')
		st.caption('Resolution in XY Plane must be more than 0', unsafe_allow_html = False)
		st.markdown("")

	with right_column3:

		st.number_input('Resolution in Z direction (micro m)', key = '-ResolutionZDirectionKey-', min_value = 0.0, value = 0.0, step = 0.1, format = '%0.1f')
		st.caption('Resolution in Z direction must be more than 0', unsafe_allow_html = False)
		st.markdown("")

	st.markdown("""---""")

	###############################################################

	st.subheader(':blue[Select Objective and Zoom information]')

	AllObjectives = ['1x', '4x', '12x']

	AllZoomInfo = ['0.6x', '1x', '1.66x', '2.5x']

	left_column4, right_column4  = st.columns(2)

	with left_column4:

		st.selectbox('Objective', AllObjectives, label_visibility = "visible", key = '-ObjectiveKey-')

	with right_column4:

		st.selectbox('Zoom', AllZoomInfo, label_visibility = "visible", key = '-ZoomKey-')

	st.markdown("""---""")

	###############################################################

	st.subheader(':blue[Select Sheet Width information]')

	st.caption('Sheet Width must be more than 0%', unsafe_allow_html = False)

	st.markdown("")

	st.slider('Sheet Width (%)', min_value = 0, max_value = 100, value = 0, step = 5, format = '%d', label_visibility = "visible", key = '-SheetWidthKey-')

	st.markdown("""---""")

	###############################################################

	st.subheader(':blue[Additional Comments]')

	st.text_area('Additional Comments', placeholder = 'None', label_visibility = 'collapsed', key = '-AdditionalCommentsKey-')

	###############################################################

	# Submit the form

	submitted = st.form_submit_button('Submit', help = 'This will submit and clear the form')

	st.markdown("")

	###############################################################

	if submitted:

		SampleKey = st.session_state['-SampleIDKey-']

		if (str(SampleKey) == ""):

			ErrorMessage = st.error('Sample ID or Barcode should not be empty', icon = None)
			time.sleep(SleepTime)
			ErrorMessage.empty()
			st.stop()

		####################

		FolderPathKey = st.session_state['-FolderPathKey-']
		extensions_allowed = [".tif", ".tiff"]
		try:
			all_files = os.listdir(FolderPathKey)
			tiff_files = [i for i in all_files if i.endswith(tuple(extensions_allowed))]
		except:
			ErrorMessage = st.error('Incorrect folder path', icon = None)
			time.sleep(SleepTime)
			ErrorMessage.empty()
			st.stop()

		####################

		All_Channel_Keys = []
		for i in range(1, len(ChannelNames) + 1):
			All_Channel_Keys.append(st.session_state[f'-Channel{i}Key-'])

		Active_Channels = All_Channel_Keys.count('Yes')
		if (int(Active_Channels) == 0):
			
			ErrorMessage = st.error('Select at least 1 active channel', icon = None)
			time.sleep(SleepTime)
			ErrorMessage.empty()
			st.stop()

		####################

		NumberChannelsKey = st.session_state['-NumberChannelsKey-']
		if (int(NumberChannelsKey) != int(Active_Channels)):
			ErrorMessage = st.error('Number of channels should be equal to the number of "Yes" for the active channels', icon = None)
			time.sleep(SleepTime)
			ErrorMessage.empty()
			st.stop()

		if (int(NumberChannelsKey) == 0):
			ErrorMessage = st.error('Number of channels should be more than 0', icon = None)
			time.sleep(SleepTime)
			ErrorMessage.empty()
			st.stop()

		####################

		All_Aperture_Keys = []
		for i in range(1, len(ChannelNames) + 1):
			All_Aperture_Keys.append(st.session_state[f'-Aperture{i}Key-'])

		####################

		All_ExposureTime_Keys = []
		for i in range(1, len(ChannelNames) + 1):
			All_ExposureTime_Keys.append(st.session_state[f'-ExposureTime{i}Key-'])

		# Run sanity checks from the function SanityChecks:

		try:

			SanityChecks(All_Channel_Keys, All_Aperture_Keys, All_ExposureTime_Keys)
		
		except ValueError as e:
			
			ErrorMessage = st.error(str(e), icon = None)
			time.sleep(SleepTime)
			ErrorMessage.empty()
			st.stop()

		####################

		ResolutionInXYPlaneKey = st.session_state['-ResolutionInXYPlaneKey-']
		if (float(ResolutionInXYPlaneKey) <= 0):
			ErrorMessage = st.error('Resolution in XY Plane should be more than 0', icon = None)
			time.sleep(SleepTime)
			ErrorMessage.empty()			
			st.stop()

		####################

		ResolutionZDirectionKey = st.session_state['-ResolutionZDirectionKey-']
		if (float(ResolutionZDirectionKey) <= 0):
			ErrorMessage = st.error('Resolution in Z direction should be more than 0', icon = None)
			time.sleep(SleepTime)
			ErrorMessage.empty()			
			st.stop()

		####################

		IlluminationLeftKey = st.session_state['-IlluminationLeftKey-']
		IlluminationRightKey = st.session_state['-IlluminationRightKey-']

		if (IlluminationLeftKey == False and IlluminationRightKey == False):
			ErrorMessage = st.error('Select at least one option for the illuminations', icon = None)
			time.sleep(SleepTime)
			ErrorMessage.empty()			
			st.stop()

		###############################################################

		ObjectiveKey = st.session_state['-ObjectiveKey-']
		ZoomKey = st.session_state['-ZoomKey-']
		SheetWidthKey = st.session_state['-SheetWidthKey-']

		if (int(SheetWidthKey) == 0):
			ErrorMessage = st.error('Sheet Width should be more than 0', icon = None)
			time.sleep(SleepTime)
			ErrorMessage.empty()			
			st.stop()

		###############################################################

		# Start executing the form now that all sanity checks are completed

		PersonKey = st.session_state['-PersonKey-']
		DateKey = st.session_state['-DateKey-']

		AdditionalCommentsKey = st.session_state['-AdditionalCommentsKey-']

		#######################################################

		try:

			result = zip(ComboNames, NameIDs)

			filtered = [(a, b) for a, b in zip(ComboNames, NameIDs) if a == PersonKey]

			NamePicked, NameIDPicked = zip(*filtered)

		except:

			ErrorMessage = st.error('Error with name IDs and First/Last names. Please contact the admin(s) for help.', icon = None)
			time.sleep(SleepTime)
			ErrorMessage.empty()			
			st.stop()


		filtered = []

		try:

			filtered = [(a, b, c, d, e) for a, b, c, d, e in zip(ChannelNames, ChannelIDs, All_Channel_Keys, All_Aperture_Keys, All_ExposureTime_Keys) if c == 'Yes']

			ChannelNamesPicked, ChannelIDsPicked, ChannelsPicked, AperturesPicked, ExposureTimesPicked = zip(*filtered)

		except:

			ErrorMessage = st.error('Error with picking details regarding channels. Please contact the admin(s) for help.', icon = None)
			time.sleep(SleepTime)
			ErrorMessage.empty()			
			st.stop()

		#######################################################

		try:

			sample_rec = db.execute_query(f"FIND RECORD Sample WITH sample_id = '{SampleKey}'", unique = True)

		except:

			ErrorMessage = st.error('Error with finding the requested specimen in the Linkahead DB! Please contact the admin(s) for help.', icon = None)
			time.sleep(SleepTime)
			ErrorMessage.empty()			
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

		rec.add_property(name = "objective", value = ObjectiveKey)
		rec.add_property(name = "zoom", value = ZoomKey)

		rec.add_property(name = "sheet_width", value = int(SheetWidthKey))

		rec.add_property(name = "additional_comments", value = AdditionalCommentsKey)

		#######################################################

		# Insert records to the CaosDB server

		st.info('Uploading metadata now.')

		try:

			rec.insert()

		except:
			
			ErrorMessage = st.error('Error with inserting records in the Linkahead DB. Check the Sample ID/Barcode again or  contact the admin(s) for help.', icon = None)
			time.sleep(SleepTime)
			ErrorMessage.empty()			
			st.stop()

		#######################################################

		ProgressBarText = st.empty()
		ProgressBar = st.progress(0)

		for percent_complete in range(100):

			time.sleep(0.1)
			ProgressBar.progress(percent_complete + 1)
			ProgressBarText.caption(f'{percent_complete + 1}% metadata uploaded')

		SuccessMessageMetadata = st.success('Successfully uploaded metadata, please wait while the images are uploaded.')

		#######################################################

		st.markdown("""---""")

		time.sleep(SleepTime)

		#######################################################

		# Upload images to Amazon S3 bucket

		st.info('Uploading images now.')

		#######################################################

		# Initialize the logger
		logger = logging.getLogger()
		logger.setLevel(logging.ERROR)

		ProgressBarText = st.empty()
		ProgressBar = st.progress(0)

		for i in range(len(tiff_files)):

			# amazon_bucket_target_name = type_of_scan + '/' + SampleKey + '/' + str(tiff_files[i])

			amazon_bucket_target_name = SampleKey + '/' + type_of_scan + '/' + str(tiff_files[i])

			try:

				make_multipart_upload(tiff_files[i], bucket_name, amazon_bucket_target_name, FolderPathKey)

				time.sleep(0.1)
				ProgressBar.progress((i+1)/len(tiff_files))
				ProgressBarText.caption("{}% images uploaded ({} images out of {} images)".format(int(100*(i+1)/len(tiff_files)), i+1, len(tiff_files)))

			except Exception as e:
				logger.error("Failed to upload %s", tiff_files[i], exc_info=True)
				pass

		#######################################################

		s3 = boto3.resource('s3',endpoint_url=AMAZON_S3_ENDPOINT_URL, aws_access_key_id=AMAZON_S3_ACCESS_KEY, aws_secret_access_key=AMAZON_S3_SECRET_KEY)

		# Create a Bucket object representing the specified Amazon S3 bucket
		bucket = s3.Bucket(AMAZON_S3_BUCKET)

		# prefix = type_of_scan + '/' + SampleKey
		prefix = SampleKey + '/' + type_of_scan

		# Get list of objects in the PCT directory
		objects = list(bucket.objects.filter(Prefix=prefix))

		# Get total number of files in the bucket
		total_files = len(objects)

		filename = 'Uploaded_files_to_S3.txt'

		if os.path.exists(filename):
			os.remove(filename)

		with open(filename, 'w') as file:
			# Write the first line with timestamp
			timestamp = datetime.now().strftime('%d %B %Y at %H:%M hrs')
			file.write('Log generated on ' + timestamp + '\n')
			file.write('\n')

			# Loop over each object in the bucket and write its name and upload date to the text file
			for i in range(total_files):

				obj = objects[i]

				# Write object name and upload date to text file
				file.write(obj.key + ' ' + obj.last_modified.strftime('(Created on : ' + '%d %B %Y at %H:%M hrs UTC time)') + '\n')

		#######################################################

		print('Successfully uploaded all images and metadata. Close the program to start a new upload.')

		SuccessMessageImagesUpload = st.success('Successfully uploaded all images. Close the program to start a new upload.')

		st.stop()
	
#######################################################################
