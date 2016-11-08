import pychromecast
import pymysql
import youtube_dl
import sys
import subprocess
import time
from decimal import *

# Default ChromeCast Name
chromecast_name = "Living Room"

# Connect String
db = pymysql.connect("localhost", user="openhab", passwd="openhab", db="alexa", connect_timeout=10)


# Sets up The Chromecast For Use (Will Run any time there is an issue connecting to the Chromecast)
def setup():
	chromecastList = list(pychromecast.get_chromecasts_as_dict().keys())
	if chromecastList == []:
		raise Exception("We didn't find any Chromecasts...")
	else:
		print ("Found ChromeCast: " + str(chromecastList))
		return chromecastList


if chromecast_name is None:
	chromecast_name = setup()[0]

cast = pychromecast.get_chromecast(friendly_name=chromecast_name)
youtube_extractor = youtube_dl.YoutubeDL()


# Send Video Function
def sendVideo(url):
	# Sets up the Chromecast's Media Controller
	mc = cast.media_controller
	# Uses Youtube-Dl to get the Stream URL for the Video to send to Chromecast
	try:
		info = youtube_extractor.extract_info(url, download=False)
		# Sends the Video
		mc.play_media(info['url'], 'video/mp4')
		print ("Video sent to Chromecast!")
		return "success"
	except:
		print "Unexpected error:", sys.exc_info()[0]
		return "success"


def volumeSet(Volnum):
	# Set's the Decimal Modules Rounding
	getcontext().prec = 3
	# Puts the Volume into something the ChromeCast can Understand
	actual_volume = Decimal(int(Volnum)) / Decimal(100)
	# Converts it to a float
	actual_volume = float(actual_volume)

	# Sends the set volume command to the Chromecast
	cast.set_volume(actual_volume)
	print ("Volume set to: " + str(Decimal(int(Volnum)) / Decimal(100)))
	return "success"


def pauseVideo():
	mc = cast.media_controller

	# Sends Pause Command To Chromecast
	mc.pause()
	print ("Video Paused.")
	return "success"


def resumeVideo():
	mc = cast.media_controller

	# Resumes Playback
	mc.play()
	print ("Video Resumed.")
	return "success"


def dbConnect():

	# Set's up the connection to run commands
	cur = db.cursor()

	# MySQL Query that selects the most recent command
	cur.execute("SELECT * FROM commands ORDER BY TIMESTAMP DESC LIMIT 1 ;")

	# Loops through the row to see what command it was to send it to the right function
	for row in cur.fetchall():
		if row[1] == "play":
			url = row[2]
			print ("user wants to watch: " + url)
			idOfQuert = row[0]
			status = sendVideo(url)

		if row[1] == "pause":
			idOfQuert = row[0]
			print("user wants to pause playback")
			status = pauseVideo()

		if row[1] == "resume":
			idOfQuert = row[0]
			print("user wants to resume playback")
			status = resumeVideo()

		if row[1] == "volume":
			idOfQuert = row[0]
			volume = row[2]
			print("user wants to set volume to " + str(volume))
			status = volumeSet(volume)

		if status == "success":
			# Deletes the Row when Done
			cur.execute("DELETE FROM commands WHERE id=" + str(idOfQuert))
			print("Command Completed.")

# Loops Continuously to get new commands.
while True:
	dbConnect()
	time.sleep(2)


