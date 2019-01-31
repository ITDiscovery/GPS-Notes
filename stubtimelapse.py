#! /usr/bin/python
# Written by Peter Nichols to take time lapse pictures and geotag it. http://www.itdiscovery.info
# Kicked off by remote SSH and static IP or autofire on headless
# Used to check function code and hardware.
# Presetup of camera required first

slptime = 0
import sys
import re
import os
import time
import pexif 
import argparse

#Parse the command line for additional arguments
parser = argparse.ArgumentParser(description='Python script that captures pictures from the camera and then makes a time lapse video.')
parser.add_argument('-i','--interval', default="12", help='-i --interval [1] in seconds for the JPG files.',required=False)
parser.add_argument('-j','--framecount', default="200", help='-j --framecount [200] How many JPG files to take.',required=False)
parser.add_argument('-d','--debug', default=1, help='Debug -d --debug [0] 0=off, 1=screen, 2=logfile',required=False)
parser.add_argument('-c','--caption', default="Raspberry Pi Track", help='-c --caption [Raspberry Pi Track] Text placed into ImageDescription tag.',required=False)
parser.add_argument('-n', '--devname', default="/dev/video0", help='-n --devname [/dev/video0] Device Name',required=False)
parser.add_argument('-f','--fname', default="/home/pi/tlapse/tlapsepic", help='-f --file [/home/pi/gpspics] The directory and file header name for the JPG files.',required=False)
parser.add_argument('-l','--location', default="32.855500 -97.2179", help='-l --location [32.855500 -97.2179] for the JPG files.',required=False)
args = parser.parse_args()

intertime = float(args.interval)
dbug = int(args.debug)
imgcaption = args.caption
devname = args.devname
fname = args.fname
framecount = args.framecount
latlong = args.location
lapsetimestart = time.time()
lapsetime = time.time()

#Splice out location into Longtitude
latlong = args.location
loclat = 32.855500
loclong = -97.2179

#Turns off flash
#gphoto2 --debug --debug-logfile=my-logfile.txt --set-config /main/capturesettings/flashmode=1

#Set up Camera

cmdstr="gphoto2 --set-config /main"

oserr = os.system(cmdstr)
if dbug==1:
     print (cmdstr)

#clear the terminal if in debug mode (optional)
if dbug==1:
     os.system('clear') 

# Function definition is here
def framesnap(oserr):
    #Take a Picture and add to the log file
    temptime = time.strftime("%Y%m%d%H%M%S")   
    #cmdstr = "fswebcam --no-banner -r 1280x720 -q -d "+ devname + " " + fname + "-" + temptime + ".jpg"
    cmdstr = "gphoto2 --capture-image-and-download --filename " + fname + "-" + temptime + ".jpg"
    if dbug==1:
        print (cmdstr)
    #Sends the command to the OS and return with the exit status
    oserr = os.system(cmdstr)
    #Tag the file with the coords
    ef = pexif.JpegFile.fromFile(fname + "-" + temptime + ".jpg")
    img = ef.get_exif(create=True)
    img.primary.ImageDescription = imgcaption
    img.primary.DateTime = time.strftime("%H:%M:%S  %d/%m/%Y")
    img.primary.Software = "Raspberry Pi Timelapse.py"
    ef.set_geo(loclat,loclong)
    ef.writeFile(fname + "-" + temptime + ".jpg")
    if dbug==1:
        print (fname + "-" + temptime + ".jpg Tagged.")
    #Update the log file used by mencoder
    fhandle = open(fname + ".log","a")
    fhandle.write(fname + "-" + temptime + ".jpg/n")
    fhandle.close
    if dbug==1:
        print (fname + "-" + temptime + ".jpg logged.")
    return

def videostitch(oserr):
    #Encode the video   
    cndstr = "mencoder -nosound -ovc lavc -lavcopts vcodec=mpeg4:aspect=16/9:vbitrate=8000000 -vf scale=1280:720 -o " + fname
    cmdstr = cmdstr + ".avi -mf type=jpeg:fps=24 mf://@"  + fname + ".log"
    #Sends the command to the OS and return with the exit status
    oserr = os.system(cmdstr)
    if dbug==1:
        print (cmdstr)
    #Remove all the pics
    fhandle = open(fname + ".log","r")
    for strline in fhandle:
        cmdstr = "rm " + strline
        oserr = os.system(cmdstr)
    #Remove the log file
    oserr = os.system("rm " + fname + ".log")
    return

i=0
while (i < framecount):
    j = framesnap(0)
    i=i+1
    time.sleep(intertime)

#We've captured some pictures, time to crank out a video file
j=videostitch(0)

print ("Done.\nExiting.")
