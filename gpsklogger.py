#! /usr/bin/python
# Written by Dan Mandle http://dan.mandle.me September 2012
# Modified by Peter Nichols for output to Google Mapmaker compatible kml file http://www.itdiscovery.info
# Added headless operation with status LED, and untested stub for switch to exit from program (OS restarts it on exit would create new track file)
# Added command line parser with help (requires Python 2.7)
# License: GPL 2.0

from gps import *
from time import *
import time
import threading
from math import radians, cos, sin, asin, sqrt
import sys
import argparse

# LED Hooked to Pin 11, Switch Hooked to Pin 12
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(11, GPIO.OUT, initial=GPIO.LOW)
#GPIO.setup(12, GPIO.IN)

def haversine(lon1, lat1, lon2, lat2):
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6367 * c
    return km

#Initialize Temp Variables
datestmp = time.strftime("%Y%m%d%H%M%S")
gpsd = None
slptime = 0
startflg = 0
dbug = 0
tlat = 0
tlong = 0
dist = 0 
ttime = 0

#Command line parser 
parser = argparse.ArgumentParser(description='Python script that captures GPS coords in a Mapmaker compatible KML format.')
parser.add_argument('-d','--debug', default=0, help='Debug -d --debug [0] 0=off, 1=screen, 2=logfile',required=False)
parser.add_argument('-i','--interval',default=2, help='-i --interval [2] Interval between GPS data captures, in seconds.', required=False)
parser.add_argument('-m','--mindist', default=1, help='-m --mindist [1] Minimum distance required for a new capture (in meters).',required=False)
parser.add_argument('-c','--color', default="800000FF", help='-c --color [800000FF] Line color input into the KML file.',required=False)
parser.add_argument('-f','--file', default="/home/pi/gpsdata", help='-f --file [/home/pi/gpsdata] The directory and file header name for the KML files.',required=False)
args = parser.parse_args()

#Get the arguments for this run
dbug = int(args.debug)
slpinterval = float(args.interval)
mindist = float(args.mindist)
lncolor = args.color
fname = args.file

#Open a log entry for this run
if dbug==2:
     fhandle = open("/home/pi/kmllogger.log","a")
     fhandle.write("Start:" + time.strftime("%H:%M %m-%d") + "\n")
     fhandle.close

#Write out the kml header
fhandle = open(fname + datestmp + ".kml", "w")
fhandle.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
fhandle.write("<kml xmlns=\"http://earth.google.com/kml/2.2\">\n")
fhandle.write("<Document>\n")
fhandle.write("<name>Paths</name>\n")
fhandle.write("<description><![CDATA[trail hiking\n")
fhandle.write("RPI" + datestmp + "\n")
fhandle.write("Created by GPSKLogger on Raspberry Pi.]]>\n")
fhandle.write("</description>\n")
fhandle.write(" <Style id=\"style1\">\n")
fhandle.write("    <IconStyle>\n")
fhandle.write("      <Icon>\n")
fhandle.write("        <href>http://maps.google.com/mapfiles/kml/paddle/grn-circle_maps.png</href>\n")
fhandle.write("      </Icon>\n")
fhandle.write("    </IconStyle>\n")
fhandle.write("  </Style>\n")
fhandle.write("  <Style id=\"style1\">\n")
fhandle.write("    <LineStyle>\n")
fhandle.write("      <color>800000FF</color>\n")
fhandle.write("      <width>5</width>\n")
fhandle.write("    </LineStyle>\n")
fhandle.write("  </Style>\n")
fhandle.write("  <Style id=\"style1\">\n")
fhandle.write("    <IconStyle>\n")
fhandle.write("      <Icon>\n")
fhandle.write("        <href>http://maps.google.com/mapfiles/kml/paddle/red-circle_maps.png</href>\n")
fhandle.write("      </Icon>\n")
fhandle.write("    </IconStyle>\n")
fhandle.write("  </Style>\n")
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
          #Check if this is first time through loop with good data
          if startflg==0:
               #Write the KML for the first good Coord
               fhandle = open(fname + datestmp + ".kml", "a")
               fhandle.write("<Placemark>\n")
               fhandle.write("   <name>RPI" + datestmp + "(Start) </name>\n")
               fhandle.write("   <description><![CDATA[]]></description>\n")
               fhandle.write("   <styleUrl>#style1</styleUrl>\n")
               fhandle.write("   <Point>\n")
               fhandle.write("      <coordinates>"+str(gpsd.fix.longitude) + ",")
               fhandle.write(str(gpsd.fix.latitude) + ",")
               fhandle.write(str(gpsd.fix.altitude) + "</coordinates>\n")
               fhandle.write("   </Point>\n")
               fhandle.write("</Placemark>\n")
               #Write out the KML for the rest of the track
               fhandle.write("<Placemark>\n")
               fhandle.write("   <name>RPI" + datestmp + "</name>\n")
               fhandle.write("   <description><![CDATA[]]></description>\n")
               fhandle.write("   <styleUrl>#style1</styleUrl>\n")
               fhandle.write("   <LineString>\n")
               fhandle.write("       <extrude>1</extrude>\n")
               fhandle.write("       <tessellate>1</tessellate>\n")
               fhandle.write("       <altitudeMode>clamptoground</altitudeMode>\n")
               fhandle.write("       <coordinates>\n")
               #Close the file guarenteeing a write in case we get shutdown
               fhandle.close
               if dbug==2:
                   fhandle = open("/home/pi/kmllogger.log","a")
                   fhandle.write("Header Write:" + time.strftime("%H:%M %m-%d") + "\n")
                   fhandle.close
               #Make sure this is run once
               startflg = 1
          #Compute Distance between last point and this point
          dist = haversine(tlong,tlat,gpsd.fix.longitude,gpsd.fix.latitude) * 1000 
          if dist > mindist:
               #Turn on the LED
               GPIO.output(11, True)
               #Write the longtitude, latitude and then altitude
               fhandle = open(fname + datestmp + ".kml", "a")
               fhandle.write("       "+str(gpsd.fix.longitude) + ",")
               fhandle.write(str(gpsd.fix.latitude) + ",")
               fhandle.write(str(gpsd.fix.altitude) + "\n")
               fhandle.close
               #Reset the position
               tlat = gpsd.fix.latitude
               tlong = gpsd.fix.longitude
               ttime = gpsd.utc
               if dbug==2:
                    fhandle = open("/home/pi/kmllogger.log","a")
                    fhandle.write("Coord-Write:" + time.strftime("%H:%M %m-%d"))
                    fhandle.write(" Lat:" + str(tlat) + " Long:" + str(tlong) + "\n")
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
          
          #Take a nap for # of secs, this will include taking a picture
          #This would be a good place to look for the GPIO switch pushbutton push
          slptime = time.time()
          while (time.time() < slptime + slpinterval):
               #Exit on switch
	           #if GPIO.input(12)=1:
		          #raise SystemExit, 0
               j=0               
          #time.sleep(slpinterval)           
          if dbug==2:
               fhandle = open("/home/pi/kmllogger.log","a")
               fhandle.write("Loop:" + time.strftime("%H:%M:%S %m-%d"))
               fhandle.write(" Lat:" + str(tlat) + " Long:" + str(tlong) + "\n")
               fhandle.close
          GPIO.output(11,False)
  except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    if dbug<>0:
      print "\nKilling Thread..."
    #Close out the KML file
    fhandle = open(fname + datestmp + ".kml", "a")
    fhandle.write("       </coordinates>\n")
    fhandle.write("   </LineString>\n")
    fhandle.write("</Placemark>\n")
    fhandle.write("<Placemark>\n")
    fhandle.write("   <name>RPI" + datestmp + "(End) </name>\n")
    fhandle.write("   <description><![CDATA[]]></description>\n")
    fhandle.write("   <styleUrl>#style1</styleUrl>\n")
    fhandle.write("   <Point>\n")
    fhandle.write("      <coordinates>"+str(gpsd.fix.longitude) + ",")
    fhandle.write(str(gpsd.fix.latitude) + ",")
    fhandle.write(str(gpsd.fix.altitude) + "</coordinates>\n")
    fhandle.write("   </Point>\n")
    fhandle.write("</Placemark>\n")
    fhandle.write("</Document>\n")
    fhandle.write("</kml>\n")
    fhandle.close()
    if dbug==2:
         fhandle = open("/home/pi/kmllogger.log","a")
         fhandle.write("End:" + time.strftime("%H:%M %m-%d") + "\n")
         fhandle.close
    gpsp.running = False
    gpsp.join() # wait for the thread to finish what it's doing

    #Close out the LED
    GPIO.cleanup()
  print "Done.\nExiting."
