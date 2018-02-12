#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import json
import requests
import datetime
from time import sleep
from flask import Flask, request, make_response, render_template
# -*- coding: utf-8 -*-
'''
	sprengmi 2017-08-4
	issnow
'''

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def main():
	
	url_iss = "http://api.open-notify.org/iss-now.json?"
	post = "xxx"
	refresh = 240	#seconds
	
	#check = (requests.get(url-iss).status_code == 200)
	
	### API keys ###
	#per google api key 2500 req / day = 1.736/min
	#using 3 keys = 5 / min = every 12 seconds
	geooglecode = [ 'xxx',\
					'xxx',\
					'xxx']
	#60 calls / min
	openweathermap = 'xxx'
	geonames = 'xxx'
	#################
	
	#set count to positive number if you want script to call a specific number of timestamp
	#	-1 for continuous run
	count = -1
	
	while count != 0:
		####################
		###ISS Lat & Long###
		####################
		try:
			#Get json from ISS api
			issnow = requests.get(url_iss).json()
			if issnow['message'] == "success":		#check for valid return
				timestamp = issnow['timestamp']		#Get timestamp
				#Convert timestamp for power bi
				dt = datetime.datetime.fromtimestamp(int(timestamp)).strftime("%Y-%m-%dT%H:%M:%S%Z")
				lat = 	float(issnow['iss_position']['latitude'])		#Get Latitude
				long = 	float(issnow['iss_position']['longitude'])	#Get Longitute	
		except:
			print 'cannot access iss api'
			print issnow['message']
			print issnow
			#return make_response("goodbye world", 500,)
			#raise
		
		########################
		###OpenWeatherMap API###
		########################
		url_owm = 'http://api.openweathermap.org/data/2.5/weather?units=imperial&lat=' + str(lat) + '&lon=' + str(long) + '&appid=' + openweathermap
		print url_owm
			
		try:
			weather = requests.get(url_owm).json()
			temp = weather['main']['temp']
			tempstr =  (str(temp)) + u'\N{DEGREE SIGN}F'
			humidity = weather['main']['humidity']
			clouds = weather['clouds']['all']
			cond = weather['weather'][0]['description']
		except:
			print 'cannot access owm api'
			#return make_response("goodbye world", 500,)
			#raise
		
		######################################
		### Google reverse geocode request ###
		######################################
		url_geo_0 = 'https://maps.googleapis.com/maps/api/geocode/json?latlng=' + str(lat) + ',' + str(long) + '&key=' + geooglecode[0]
		url_geo_1 = 'https://maps.googleapis.com/maps/api/geocode/json?latlng=' + str(lat) + ',' + str(long) + '&key=' + geooglecode[1]
		url_geo_2 = 'https://maps.googleapis.com/maps/api/geocode/json?latlng=' + str(lat) + ',' + str(long) + '&key=' + geooglecode[2]
		#print url_geo
		try:
			#Use 1 of 3 API keys, try a different one if first is over limit
			geoloc = requests.get(url_geo_0).json()
			if geoloc['status'] == "OVER_QUERY_LIMIT":
				geoloc = requests.get(url_geo_1).json()
				if geoloc['status'] == "OVER_QUERY_LIMIT":
					geoloc = requests.get(url_geo_2).json()
			
			###Google geocode does not return bodies of water, in case there are zero results from google
			###	use geonames/ocean lookup
			if geoloc['status'] == "ZERO_RESULTS":
				url_geo = 'http://api.geonames.org/oceanJSON?lat=' + str(lat) + '&lng=' + str(long) + '&username=' + 	geonames 
				geoloc = requests.get(url_geo).json()
				loc0 = "N/A"
				loc1 = geoloc['ocean']['name']
				loc2 = "N/A"
			#Two cases for geocode names based on detail available thru google geocode
			elif geoloc['status'] == "OK" and len(geoloc['results']) < 3:
				loc0 = "N/A"
				loc1 = geoloc['results'][0]['formatted_address'].encode('utf-8')
				loc2 = "N/A"
			elif geoloc['status'] == "OK" and len(geoloc['results']) >= 3:
				loc0 = geoloc['results'][0]['formatted_address'].encode('utf-8')
				loc1 = geoloc['results'][1]['formatted_address'].encode('utf-8')
				loc2 = geoloc['results'][2]['formatted_address'].encode('utf-8')
			else:
				loc0 = "N/A"
				loc1 = "N/A"
				loc2 = "N/A"
		except:
			print 'cannot access geo api'
			#return make_response("goodbye world", 500,)
			#raise
			
		#headers = {'content-type': "application/json",    'cache-control': "no-cache",}
		headers = {'content-type': "application/x-www-form-urlencoded",'cache-control': "no-cache"}
		
		payload = "timestamp="+str(dt)+"&lat="+str(lat)+"&long="+str(long)+\
			"&loc0="+str(loc0)+"&loc1="+str(loc1)+"&loc2="+str(loc2)+\
			"&temp="+str(temp)+"&humidity="+str(humidity)+"&clouds="+str(clouds)+"&cond="+str(cond)
			
		response = requests.request("POST", post, data=payload, headers=headers)
		print response.text
		print payload
		
		count -= 1	
			
		sleep(refresh)
	return make_response("ok", 200,)


#@app.route("/auth", methods=["GET", "POST"])
#def auth():
#	client id: 
#	client secret: 
#	return make_response("hello world", 200,)
	
	
"""

													
@app.route("/post", methods=["GET","POST"])
def listneing():
	

@app.route("/", methods=["GET", "POST"])
def hello():
	
  """
  
if __name__ == "__main__":
	main()
	app.run(debug=True)
	os.execv(__file__, sys.argv)  # Run a new iteration of the current script, providing any command line args from the current iteration.
	
