#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!/usr/bin/env python3

"""
Authors: Alejandra Montano Romero, Calli Bonin
Source Code: Rubinstein, J. L., Guo, H., Ripstein, Z. A., Haydaroglu, A., Au, A., Yip, C. M., Di Trani, J. M., Benlekbir, S. & Kwok, T. (2019). Shake-it-off: a simple ultrasonic cryo-EM specimen-preparation device. Acta Cryst. D75, 1063–1070. 
Description: This file encodes a GUI to run the C-SPAM device by calling to the CSPAMfunctions.py script.
"""


# Set up
from guizero import App, TextBox, Text, PushButton, CheckBox
from subprocess import call, Popen
import RPi.GPIO as GPIO
import CSPAMpinlist as pin
import os
import CSPAMfunctions as CSPAM
import time, threading 
os.environ.__setitem__('DISPLAY', ':0.0')

PWM0 = pin.pwm0  # this is the LED output pin using hardware PWMg512
os.system('gpio mode ' + str(PWM0) + ' pwm')
os.system('gpio pwmc 2')
os.system('gpio pwm-ms')


# Functions
def ready():
    # Readies the C-SPAM device for sample preparation by setting up GPIO and advancing the filter 
    print("starting ready process")
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin.cannon,GPIO.OUT)
    GPIO.setup(pin.plunger,GPIO.OUT)
    GPIO.setup(pin.filterposition,GPIO.OUT)
    GPIO.setup(pin.sensorpower,GPIO.OUT)
    GPIO.setup(pin.interlock,GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
    global t0
    CSPAM.filterforward(0)
    global filterforwardtime
    filterforwardtime = time.perf_counter_ns()/(10**6)
    print("ready for sample application")

def startprocess():
    # Starts C-SPAM processes by defining variables and calling to the apply and plunge scripts. An if statement is used to call to the faster apply and plunge script for fast millisecond resolution or the slower apply and plunge script for slower millisecond to second resolution. 
    print("starting process")
    retractiondelay  = float(rdelay.value)/1000
    plungedelay = float(pdelay.value)/1000
    ledint = int(ledIntensity.value)
    if donotplunge.value==1:
        abort()
    else:
        if float(ldelay.value)/1000 < 0.050:
            print("starting fast resolution process")
            leddelay = 0.043-(float(ldelay.value)/1000) #delay after plunger falls before turning on LED
            startingprocesstime = time.perf_counter_ns()/(10**6)
            CSPAM.applyandplungeFAST(retractiondelay,plungedelay,leddelay,ledint)
        else:
            print("starting slower resolution process")
            ltime= (float(ldelay.value)/1000)-(float(pdelay.value)/1000)-0.043 # time LED remains on
            startingprocesstime = time.perf_counter_ns()/(10**6)
            CSPAM.applyandplungeSLOW(retractiondelay,plungedelay,ltime,ledint)

def abort():
    # resets all processes and sets up GPIO 
    GPIO.setwarnings(False) # needs a GPIO set up each time device is run
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin.cannon,GPIO.OUT)
    GPIO.setup(pin.plunger,GPIO.OUT)
    GPIO.setup(pin.filterposition,GPIO.OUT)
    GPIO.setup(pin.sensorpower,GPIO.OUT)
    GPIO.setup(pin.interlock,GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
    CSPAM.powerdownsensors()
    CSPAM.filterreverse(0)
    CSPAM.turnoffLED(0)
    CSPAM.resetplunger(0)
    GPIO.cleanup()

    
# Design GUI    
app = App(title="C-SPAM", layout="grid")
rdelaylabel = Text(app, text="Blotting time (msec)", grid=[0,1])
rdelay      = TextBox(app, grid=[1,1], text="50")
pdelaylabel = Text(app, text="Plunge delay (msec)", grid=[0,2])
pdelay      = TextBox(app, grid=[1,2], text="50")
ldelaylabel = Text(app, text="Resolution (msec)", grid =[2,1])
ldelay = TextBox(app, grid=[3,1], text="1")

donotplunge = CheckBox(app, text="Do not plunge", grid=[0,4])
button_down = PushButton(app, command=abort, text="Abort", grid=[2,6])
button_ready = PushButton(app, command=ready, text="Ready", grid=[1,6])
button_start = PushButton(app, command=startprocess, text="Start", grid=[1,7])
button_start.bg = "green"
button_down.bg = "red"
button_ready.bg = "yellow"

ledLabel = Text(app, text="LED intensity (%)", grid=[2,2])
ledIntensity = TextBox(app, text="100", grid=[3,2])

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
app.display()

