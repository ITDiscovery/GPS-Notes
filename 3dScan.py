#!/usr/bin/python
# Import required libraries
import sys
import time
import RPi.GPIO as GPIO

 
# Use BCM GPIO references
# instead of physical pin numbers
GPIO.setmode(GPIO.BCM)
 
# Define GPIO signals to use
# Physical Stepper pins 35,38,40,37
# GPIO19,GPIO20,GPIO21,GPIO26
# Physical Laser pins 32,33,29,31
# GPIO12, GPIO13, GPIO5, GPIO6

StepPins = [19,20,21,26]
for pin in StepPins:
  GPIO.setup(pin,GPIO.OUT)
  GPIO.output(pin, False)

LaserPins = [12,13,5,6]
for pin in LaserPins:
  GPIO.setup(pin,GPIO.OUT)
  GPIO.output(,False)

#Function to move stepper motor
def motorstep(nbrsteps):
  # Define half step sequence
  # as shown in manufacturers datasheet
  Seq = [[1,0,0,1],
         [1,0,0,0],
         [1,1,0,0],
         [0,1,0,0],
         [0,1,1,0],
         [0,0,1,0],
         [0,0,1,1],
         [0,0,0,1]]
  StepCount = len(Seq)
  StepDir = 1 # Set to 1 or 2 for clockwise, Set to -1 or -2 for anti-clockwise  
  # Initialise variables
  StepCounter = 0
  for loop in range(0,nbrsteps):
    for pin in range(0,4):
        xpin=StepPins[pin]
        # Get GPIO
        if Seq[StepCounter][pin]!=0:
          GPIO.output(xpin, True)
        else:
          GPIO.output(xpin, False)
 
        StepCounter += StepDir 
    # If we reach the end of the sequence
    # start again
    if (StepCounter>=StepCount):
      StepCounter = 0
    if (StepCounter<0):
      StepCounter = StepCount+StepDir
 

# Main Loop
for onerev range(0 to 64): #Spin 360 Degrees
  print "Step"+onerev
  motorstep(8)

  # Take the first picture no laser 
  #flname="normal/000"+onerev+".jpg"
  #return_code = subprocess.call("fswebcam -r 1280x720 --no-banner -d /dev/video0 "flname,shell=True)
  #for laseron range(0,2):
  #  # Turn on LaserX, then take picture
  #  GPIO.output(LaserPins[laseron],True)
  #  flname="laser"+laseron+"/000"+onerev+".jpg"
  #  return_code = subprocess.call("fswebcam -r 1280x720 --no-banner -d /dev/video0 "flname,shell=True)
  #  GPIO.output(LaserPins[laseron],False)

