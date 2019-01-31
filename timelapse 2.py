#! /usr/bin/python
# Written by Peter Nichols to take time lapse pictures and geotag it. http://www.itdiscovery.info
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
import time
import pexif 
import argparse
import RPi.GPIO as GPIO

# LED to Pin 7
# Switch to turn on Pin 11: normally True, short to ground to make "False"
# 2ndary switch on Pin 12: normally True, short to ground to make "False"

ledport=7
btnport=11
btnport2=12
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(ledport, GPIO.OUT, initial=False)
GPIO.setup(btnport, GPIO.IN, pull_up_down = GPIO.PUD_UP)

#Parse the command line for additional arguments
parser = argparse.ArgumentParser(description='Python script that captures pictures from the camera and then makes a time lapse video.')
parser.add_argument('-i','--interval', default="1", help='-i --interval [1] in minutes for the JPG files.',required=False)
parser.add_argument('-d','--debug', default=0, help='Debug -d --debug [0] 0=off, 1=screen, 2=logfile',required=False)
parser.add_argument('-c','--caption', default="Raspberry Pi Track", help='-c --caption [Raspberry Pi Track] Text placed into ImageDescription tag.',required=False)
parser.add_argument('-n', '--devname', default="/dev/video0", help='-n --devname [/dev/video0] Device Name',required=False)
parser.add_argument('-f','--fname', default="/home/pi/tlapse/tlapsepic", help='-f --file [/home/pi/gpspics] The directory and file header name for the JPG files.',required=False)
parser.add_argument('-l','--location', default="32.855500 -97.2179", help='-l --location [32.855500 -97.2179] for the JPG files.',required=False)
args = parser.parse_args()

intertime = args.interval
dbug = int(args.debug)
imgcaption = args.caption
devname = args.devname
fname = args.fname
latlong = args.location
lapsetimestart = time.time()
lapsetime = time.time()

#Splice out location into Longtitude
latlong = args.location
loclat = 32.855500
loclong = -97.2179

#clear the terminal if in debug mode (optional)
if dbug==1:
     os.system('clear') 

# Function definition is here
def framesnap():
    #Take a Picture and add to the log file
    temptime = time.strftime("%Y%m%d%H%M%S")

   
    cmdstr = "fswebcam --no-banner -r 1280x720 -q -d "+ devname + " " + fname + "-" + temptime + ".jpg"
    if dbug==1:
        print cmdstr
    #Sends the command to the OS and return with the exit status
    oserr = os.system(cmdstr)
        
    #Tag the file with the coords
    ef = pexif.JpegFile.fromFile(fname + "-" + temptime + ".jpg")
    img = ef.get_exif(create=True)
    img.primary.ImageDescription = imgcaption
    img.primary.DateTime = time.strftime("%H:%M:%S  %d/%m/%Y")
    img.primary.Software = "Raspberry Pi Timelapse.py"
    ef.set_geo(loclat,loclog)
    ef.writeFile(fname + "-" + temptime + ".jpg")
    #Update the log file used by mencoder
    fhandle = open(fname + ".log","a")
    fhandle.write(fname + "-" + temptime + ".jpg")
    fhandle.close
    return

def videostitch():
    #Encode the video   
    cndstr = "mencoder -nosound -ovc lavc -lavcopts vcodec=mpeg4:aspect=16/9:vbitrate=8000000 -vf scale=1280:720 -o " + fname
    cmdstr = cmdstr + ".avi -mf type=jpeg:fps=24 mf://@"  + fname ".log"
    #Sends the command to the OS and return with the exit status
    oserr = os.system(cmdstr)
    #Remove all the pics
    fhandle = open(fname + ".log","r")
    for strline in fhandle:
        cmdstr = "rm " + strline
        oserr = os.system(cmdstr)
    #Remove the log file
    oserr = os.system("rm " + fname + ".log")
    return

tlapsemode = False
While True:
    #LED Status Update Check
    if timelapsemode == True:
    



    #Check for Switch On
    btnstate = GPIO.input(btnport)
    if btnstate == True:
        #Timelapse Mode now on
        tlapsemode = True
        framesnap();


    #We've captured some pictures, time to crank out a video file
    if (btnstate == False) and (tlapsemode == True)


    


              #Bottom of Button Loop (Debounce)
              time.sleep(0.1)


    #When the switch goes back off:
    #    Process that batch of files
    #    Fast Flash the LED
    #    Switch is Don't Care
    #    Back to Slow Flash LED


    #Close out the Switch
    GPIO.cleanup()
  print "Done.\nExiting."
