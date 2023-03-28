import numpy as np

import os
import json
import csv

import sys
# Don't generate the __pycache__ folder locally
sys.dont_write_bytecode = True 
# Print exception without the buit-in python warning
sys.tracebacklimit = 0 

import caosdb as db
import urllib3
#Disable the HTTPS warnings for CaosDB authentication
urllib3.disable_warnings() 

import datetime

##############################################

from .. import PASSWORDS

##############################################

def make_json_file(json_file):

	# remove LSM_overview.json files from the current working directory

	if os.path.isfile(json_file):
		os.remove(json_file)

	##############################################

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

		print()

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

			print()

		# If connection still fails, raise an exception
		except:
			raise Exception('Unsuccessful connection with the Linkahead DB. Contact the admin(s) for help.')

	##############################################

	# Find all LSM scan entries in the database

	which_type_of_scan = 'LSM_SCAN'

	LSM_entries = db.execute_query('FIND RECORD ' + which_type_of_scan)

	##############################################

	global_entries = []

	current_index = 1

	for single_entry in LSM_entries:
		
		SampleID = list(single_entry.get_property_values('Sample'))[0]

		SampleID = str(int(SampleID))

		##############################################

		SampleName = list(db.execute_query(f"FIND SAMPLE WITH id = '{SampleID}'", unique=True).get_property_values('name'))[0]
		
		if SampleName is None:
			SampleName = 'None'

		SampleName = str(SampleName)

		##############################################

		UploaderID = list(single_entry.get_property_values('operator'))[0]

		UploaderID = str(int(UploaderID))

		##############################################

		GivenName = list(db.execute_query(f"FIND PERSON WITH id = '{UploaderID}'", unique=True).get_property_values('given_name'))[0]

		GivenName = str(GivenName)

		##############################################

		FamilyName = list(db.execute_query(f"FIND PERSON WITH id = '{UploaderID}'", unique=True).get_property_values('family_name'))[0]

		FamilyName = str(FamilyName)

		##############################################

		EmailAddress = list(db.execute_query(f"FIND PERSON WITH id = '{UploaderID}'", unique=True).get_property_values('email_address'))[0]

		EmailAddress = str(EmailAddress)

		##############################################

		Date = list(single_entry.get_property_values('date'))[0]

		Date = str(Date)

		##############################################

		DeltaPixelXY = list(single_entry.get_property_values('delta_pixel_xy'))[0]

		DeltaPixelXY = str(round(DeltaPixelXY, 2))

		##############################################

		DeltaPixelZ = list(single_entry.get_property_values('delta_pixel_z'))[0]

		DeltaPixelZ = str(round(DeltaPixelZ, 2))

		##############################################

		NumberOfChannels_raw = list(single_entry.get_property_values('number_of_channels'))[0]

		NumberOfChannels = str(int(NumberOfChannels_raw))

		##############################################

		wavelengths_only = []

		for single_filter in list(single_entry.get_property_values('filters')[0]):
			wavelengths_only.append((list(db.execute_query(f"FIND Wavelengths WITH id = '{single_filter}'", unique=True).get_property_values('name'))[0]))

		str_wavelengths = ", ".join(wavelengths_only)

		##############################################

		if len(wavelengths_only) != int(NumberOfChannels_raw):

			raise Exception('Number of channels is not equal to number of wavelengths isolated')

		##############################################

		IlluminationLeft = list(single_entry.get_property_values('illumination_left'))[0]

		IlluminationLeft = str(IlluminationLeft)

		##############################################

		IlluminationRight = list(single_entry.get_property_values('illumination_right'))[0]

		IlluminationRight = str(IlluminationRight)

		##############################################

		Apertures = list(single_entry.get_property_values('apertures')[0])

		Apertures = np.int_(Apertures)

		Apertures = ", ".join(str(x) for x in Apertures)

		##############################################

		ExposureTimes = list(single_entry.get_property_values('exposure_times')[0])

		ExposureTimes = np.int_(ExposureTimes)

		ExposureTimes = ", ".join(str(x) for x in ExposureTimes)

		##############################################

		Objective = list(single_entry.get_property_values('objective'))[0]

		##############################################

		Zoom = list(single_entry.get_property_values('zoom'))[0]

		##############################################

		SheetWidth = list(single_entry.get_property_values('sheet_width'))[0]

		SheetWidth = str(SheetWidth)

		##############################################

		AdditionalComments = list(single_entry.get_property_values('additional_comments'))[0]

		if len(AdditionalComments) == 0:
			AdditionalComments = 'None'

		AdditionalComments = str(AdditionalComments)

		##############################################

		# create a dictionary to store the properties
		single_entry_data = {
			"#": current_index,
			"Scan Type": which_type_of_scan,
			"Sample ID": SampleID,
			"Sample Name / Barcode": SampleName,
			"Uploader ID": UploaderID,
			"Uploader First Name": GivenName,
			"Uploader Family Name": FamilyName,
			"Uploader Email Address": EmailAddress,
			"Upload Date [YYYY-MM-DD]": Date,
			"Resolution in XY Plane [&mu;m])": DeltaPixelXY,
			"Resolution in Z direction [&mu;m]": DeltaPixelZ,
			"Number of Channels": NumberOfChannels,
			"Wavelengths": str_wavelengths,
			"Illumination Right": IlluminationRight,
			"Illumination Left": IlluminationLeft,
			"Aperture [%]": Apertures,
			"Exposure Times [&mu;s]": ExposureTimes,
			"Objective": Objective,
			"Zoom": Zoom,
			"Sheet Width [%]": SheetWidth,
			"Additional Comments": AdditionalComments
			}

		##############################################

		global_entries.append(single_entry_data)

		current_index = current_index + 1

	##############################################

	# create the JSON file
	with open(json_file, 'w') as outfile:
		json.dump(global_entries, outfile)

	print(f"{json_file} file successfully created!")

############################################################################################################

def convert_json_to_csv(json_file, csv_file):
	"""
	Convert a JSON file to a CSV file and save it.

	Args:
		json_file (str): Path to the JSON input file.
		csv_file (str): Path to the CSV output file.
	"""

	if os.path.isfile(csv_file):
		os.remove(csv_file)

	# Load the JSON data from a file
	with open(json_file, 'r') as f:
		data = json.load(f)

	# Get the header fields from the JSON keys
	header = list(data[0].keys())

	# Write the data to the CSV file
	with open(csv_file, 'w', newline='') as f:
		writer = csv.DictWriter(f, fieldnames=header)
		writer.writeheader()
		writer.writerows(data)

	print(f"CSV file '{csv_file}' exported successfully!")

############################################################################################################

def convert_json_to_html(json_file, html_file):
	"""
	Convert a JSON file to an HTML table and write the result to an output file.

	Args:
		json_file (str): Path to the JSON input file.
		html_file (str): Path to the HTML output file.

	Raises:
		ValueError: If the input file is not a valid JSON file.
	"""

	if os.path.isfile(html_file):
		os.remove(html_file)

	# Load the JSON data from a file
	try:
		with open(json_file, 'r') as f:
			data = json.load(f)
	except json.JSONDecodeError:
		raise ValueError(f'{json_file} is not a valid JSON file.')

	# Convert the JSON data to an HTML table
	table = '<table style="border-collapse: collapse; width: 100%;">\n'
	table += '<thead>\n'
	table += '<tr style="background-color: #f2f2f2;">\n'
	for i, key in enumerate(data[0].keys()):
		if i == 0:
			table += f'<th style="padding: 8px; text-align: center; border-bottom: 1px solid #ddd; border-right: 1px solid #ddd; border-left: 1px solid #ddd; white-space: nowrap;">{key}</th>\n'
		elif i == len(data[0]) - 1:
			table += f'<th style="padding: 8px; text-align: center; border-bottom: 1px solid #ddd; border-right: 1px solid #ddd; white-space: nowrap;">{key}</th>\n'
		else:
			table += f'<th style="padding: 8px; text-align: center; border-bottom: 1px solid #ddd; border-right: 1px solid #ddd; white-space: nowrap;">{key}</th>\n'
	table += '</tr>\n'
	table += '</thead>\n'
	table += '<tbody>\n'
	for item in data:
		table += '<tr>\n'
		for i, value in enumerate(item.values()):
			if i == 0:
				table += f'<td style="padding: 8px; text-align: center; border-bottom: 1px solid #ddd; border-right: 1px solid #ddd; border-left: 1px solid #ddd;">{value}</td>\n'
			else:
				table += f'<td style="padding: 8px; text-align: center; border-bottom: 1px solid #ddd; border-right: 1px solid #ddd;">{value}</td>\n'
		table += '</tr>\n'
	table += '</tbody>\n'
	table += '</table>\n'  # Add extra \n after the table

	# Add timestamp and title to the HTML file
	title = "Overview of the uploaded metadata for the ABA project at the Max Planck Institute for Multidisciplinary Sciences, Göttingen and the Universitätsmedizin Göttingen"
	head = f'<head><title>{title}</title></head>'
	timestamp = datetime.datetime.now().strftime('%d %B %Y at %H:%M hrs')
	created_on = f"Created on {timestamp}"
	created_on_div = f'<div style="text-align: left;">{created_on}</div>\n'
	html = f'<html>{head}<body>{table}{created_on_div}</body></html>'

	# Save the HTML table to a file
	with open(html_file, 'w') as f:
		f.write(html)

	print(f"HTML file '{html_file}' exported successfully!")

############################################################################################################

if __name__ == '__main__':

	os.system('clear || cls')

	make_json_file('LSM_overview.json')

	print()

	convert_json_to_html('LSM_overview.json', 'LSM_overview.html')

	print()

	convert_json_to_csv('LSM_overview.json', 'LSM_overview.csv')

print()

############################################################################################################