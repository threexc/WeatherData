import requests
import sys
import re
import datetime
import os
import errno
import xml.etree.ElementTree as ET

# WeatherCollector will collect and tidy the necessary METAR and TAF data for
# a specified aerodrome. This is currently hard-coded to work with the NAV
# CANADA website only. This object-oriented implementation is still under
# development.
class WeatherCollector:

	def __init__(self, station, page_format='raw', language='anglais', region='can'):

		# The page of interest. Use GET calls to provide it the parameters for
		# each aerodrome
		self.url = "https://flightplanning.navcanada.ca/cgi-bin/Fore-obs/metar.cgi"

		# Default headers to mimic for scraping the page
		self.headers = {
        "user-agent": "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0"
    	}

		# The parameters to be encoded and passed to the page as part of the
		# GET request. Note that the only parameter that should ever be
		# modified (and is in fact intended to be) is the station (aerodrome).
		# The others are provided as inputs for testing and for potential
		# future-proofing
		self.params = {'Stations': station, 'format': page_format, 'Langue': language, 'Region': region}

		# class variables to hold the data for each aerodrome once it is parsed
		self.parsed_data = None
		self.metar = None
		self.taf = None


	# The core component of the WeatherCollector class. This function takes the
	# input URL and parameters, then performs the following:
	#
	# 1. Encodes the base URL and parameters while sending a GET request to the
	# page
	# 2. Removes all of the HTML formatting from the text data (string)
	# 3. Removes whitespace and leftover formatting ("&nbsp;...")
	# 4. Creates a baseline string containing all of the data before further
	# isolating the METAR and TAF content
	# 5. Splits out the TAF data and truncates it following the final "=", which
	# is found in every aerodrome reading tested
	# 6. Similarly splits out the METAR data and truncates it following the
	# final "=" character
	# 7. Sets the class variables self.parsed_data, self.metar, and self.taf
	# equal to their corresponding strings

	# TODO: Write extensive error handling into this function
	def gather_data(self):

		# Send the GET request with the base URL and parameters
		response = requests.get(self.url, params=self.params, verify=False, headers=self.headers)

		# Strip out all of the HTML formatting
		stripped = re.sub("<.*?>", "", response.text)

		# Get rid of newlines
		cleaned = stripped.replace('\n', '')

		# Remove the mysterious &nbsp; substring
		tidied = cleaned.replace('&nbsp;&nbsp;&nbsp;&nbsp;', ' ')

		# Ignore the text before the first occurrence of the substring "TAF"
		split_data = tidied.split('TAF ', 1)[1]

		# Cut out leading text again, this time up to the first occurrence of
		# the substring "METAR". This may be a redundant variable, but it is
		# left for now
		metar_taf_data = split_data.split('METAR', 1)[1]

		# Pluck the TAF from the data and remove the trailing "="
		taf = metar_taf_data.split('TAF ', 1)[1]
		fixed_taf = taf[:taf.rfind('=')]

		# Pluck the METAR from the data and remove the trailing "="
		metar = metar_taf_data.split('TAF ', 1)[0]
		fixed_metar = metar[:metar.rfind('=')]

		# Assign the collected strings to the appropriate class variables
		self.parsed_data = split_data
		self.metar = fixed_metar
		self.taf = fixed_taf

		return

	# Placeholder, may not be necessary
	def set_url(self, new_url):
		self.url = new_url

	# returns the whole string consisting of METAR and TAF data without having
	# separated them, plus the aerodrome header
	def get_weather(self):
		return self.parsed_data

	# Returns the METAR data for the aerodrome
	def read_metar(self):
		return self.metar

	# Returns the TAF data for the aerodrome
	def read_taf(self):
		return self.taf

# TODO: Rebuild the file creation and writing components of the parser


# The eventual parser class to complement the collector. Should be a parent
# class to separate METAR and TAF parser classes
class WeatherParser:
	pass