#! /usr/bin/python
# Written by Peter Nichols to take picture from a switch input and geotag it. http://www.itdiscovery.info
# Modified from code by Dan Mandle http://dan.mandle.me September 2012
# Modified by Peter Nichols for headless operation.
# License: GPL 2.0

# First let's check to see if the camera is present
# Stub based on code by meson10 at www.stackoverflow.com
# Probably a way to reduce this, but it works
slptime = 0
import sys
import re
import subprocess
device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
df = subprocess.check_output("lsusb", shell=True)
for i in df.split('\n'):
    if i:
        info = device_re.match(i)
        if info:
            dinfo = info.groupdict()
            if dinfo.pop('id')=="046d:0825":
               slptime = 1
if slptime==0:
    sys.exit()


# We have a camera, continue with the rest
import os
from gps import *
import time
import threading
import pexif 
import argparse

# LED Switch Hooked to Pin 7
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(7, GPIO.IN)

gpsd = None #seting the global variable

#Parse the command line for additional arguments
parser = argparse.ArgumentParser(description='Python script that captures GPS coords in a Mapmaker compatible KML format.')
parser.add_argument('-d','--debug', default=0, help='Debug -d --debug [0] 0=off, 1=screen, 2=logfile',required=False)
parser.add_argument('-c','--caption', default="Raspberry Pi Track", help='-c --caption [Raspberry Pi Track] Text placed into ImageDescription tag.',required=False)
parser.add_argument('-n', '--devname', default="/dev/video0", help='-n --devname [/dev/video0] Device Name')
parser.add_argument('-f','--fname', default="/home/pi/gpspics/gpspic", help='-f --file [/home/pi/gpspics] The directory and file header name for the JPG files.',required=False)
args = parser.parse_args()

dbug = int(args.debug)
imgcaption = args.caption
fname = args.fname
devname = args.devname

#Grab first state of button
btnstate = GPIO.input(7)

#Add to log file
if dbug==2:
     fhandle = open("/home/pi/kmllogger.log","a")
     fhandle.write("Start:" + time.strftime("%H:%M %m-%d") + "\n")
     fhandle.close

#clear the terminal if in debug mode (optional)
if dbug==1:
     os.system('clear') 
 
class GpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    global gpsd #bring it in scope
    gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
    self.current_value = None
    self.running = True #setting the thread running to true
 
  def run(self):
    global gpsd
    while gpsp.running:
      gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer
 
if __name__ == '__main__':
  gpsp = GpsPoller() # create the thread
  try:
    gpsp.start() # start it up
    while True:
      #It may take a second or two to get good data
      if (gpsd.fix.longitude<>0) and (gpsd.fix.longitude<>'nan'):
          #Check for Button Press
          newbtnstate = GPIO.input(7)
          if btnstate <> newbtnstate:
               #Update button state
               btnstate = newbtnstate
               #Take a picture 
               temptime = time.strftime("%Y%m%d%H%M%S")
               cmdstr = "fswebcam --no-banner -r 960x720 -q -d "+ devname + " " + fname + "-" + temptime + ".jpg"
               #Sends the command to the OS and return with the exit status
               os.system(cmdstr)
               #Tag the file with the coords
               ef = pexif.JpegFile.fromFile(fname + "-" + temptime + ".jpg")
               img = ef.get_exif(create=True)
               img.primary.ImageDescription = imgcaption
               img.primary.DateTime = time.strftime("%H:%M:%S  %d/%m/%Y")
               img.primary.Software = "Raspberry Pi Picttracker.py"
               ef.set_geo(gpsd.fix.latitude, gpsd.fix.longitude)
               ef.writeFile(fname + "-" + temptime + ".jpg")
               if dbug==2:
                    fhandle = open("/home/pi/kmllogger.log","a")
                    fhandle.write("Coord-Write:" + time.strftime("%H:%M %m-%d"))
                    fhandle.write(" Lat:" + str(gpsd.fix.latitude) + " Long:" + str(gpsd.fix.longitude) + "\n")
                    fhandle.close
          #clear the terminal if in debug mode (optional)
          if dbug==1:
              os.system('clear') 
              print
              print ' GPS reading'
              print '----------------------------------------'
              print '----------------------------------------'
              print 'latitude    ' , gpsd.fix.latitude
              print 'longitude   ' , gpsd.fix.longitude
              print 'time utc    ' , gpsd.utc,' + ', gpsd.fix.time
              print 'altitude (m)' , gpsd.fix.altitude
              print 'eps         ' , gpsd.fix.eps
              print 'epx         ' , gpsd.fix.epx
              print 'epv         ' , gpsd.fix.epv
              print 'ept         ' , gpsd.fix.ept
              print 'speed (m/s) ' , gpsd.fix.speed
              print 'climb       ' , gpsd.fix.climb
              print 'track       ' , gpsd.fix.track
              print 'mode        ' , gpsd.fix.mode
              print
              print 'distance    ' , dist
              print 'TTIME       ' , ttime
              #Bottom of Button Loop (Debounce)
              time.sleep(0.1)
  except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    if dbug<>0:
      print "\nKilling Thread..."
    if dbug==2:
         fhandle = open("/home/pi/kmllogger.log","a")
         fhandle.write("End:" + time.strftime("%H:%M %m-%d") + "\n")
         fhandle.close
    gpsp.running = False
    gpsp.join() # wait for the thread to finish what it's doing
    #Close out the Switch
    GPIO.cleanup()
  print "Done.\nExiting."
