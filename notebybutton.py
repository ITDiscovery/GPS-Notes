#! /usr/bin/python
# Written by Dan Mandle http://dan.mandle.me September 2012
# Modified by Peter Nichols for output produce a note file via switchbutton file http://www.itdiscovery.info
# Added headless operation with status LED, and untested stub for switch to exit from program (OS restarts it on exit would create new track file)
# Added command line parser with help (requires Python 2.7)
# License: GPL 2.0

from gps import *
import time
import threading
import sys
import argparse

# LED Hooked to Pin 11, Switch Hooked to Pin 7
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(7, GPIO.IN)
btnstate = GPIO.input(7)

#Initialize Temp Variables
datestmp = time.strftime("%Y%m%d%H%M")
gpsd = None

#Write out the txt header
fhandle = open("/home/pi/NotesGPS" + datestmp + ".txt", "w")
fhandle.write("Open of Note file:"+ time.strftime("%d/%m/%Y %H:%M")+ "\n")
fhandle.close
 
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
         #Now just hang out for button press
         newbtnstate = GPIO.input(7)
         if btnstate <> newbtnstate:
               #Update button state and update the file
               btnstate = newbtnstate
               fhandle = open("/home/pi/NotesGPS" + datestmp + ".txt","a")
               fhandle.write("Note Time:" + time.strftime("%H:%M:%S %m-%d") + "\n")
               fhandle.write("Lat:" + str(gpsd.fix.latitude) + ", Long:" + str(gpsd.fix.longitude))
               fhandle.write(", Alt:" + str(gpsd.fix.altitude)+ "\n")
               fhandle.close
               print "Button Press"
               #Nap for debounce
               time.sleep(1)
  except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print "\nKilling Thread..."
    fhandle = open("/home/pi/NotesGPS" + datestmp + ".txt","a")
    fhandle.write("Graceful Shutdown:" + time.strftime("%H:%M:%S %m-%d"))
    fhandle.write(" Lat:" + str(gpsd.fix.latitude) + " Long:" + str(gpsd.fix.longitude) + "\n")
    fhandle.close
    gpsp.running = False
    gpsp.join() # wait for the thread to finish what it's doing
    #Close out the LED
    GPIO.cleanup()
  print "Done.\nExiting."
