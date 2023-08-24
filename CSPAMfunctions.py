# /usr/bin/env python
# coding: utf-8

# In[4]:

#!/usr/bin/env python
# coding: utf-8

# In[ ]:

#!/usr/bin/env python3

"""
Authors: Alejandra Montano Romero, Calli Bonin
Source Code: Rubinstein, J. L., Guo, H., Ripstein, Z. A., Haydaroglu, A., Au, A., Yip, C. M., Di Trani, J. M., Benlekbir, S. & Kwok, T. (2019). Shake-it-off: a simple ultrasonic cryo-EM specimen-preparation device. Acta Cryst. D75, 1063–1070.
Description: This file contains functions to control the C-SPAM device for fast millisecond resolution of samples. Functions are designed to power up or down sensors, turn on or off LED, set LED intensity, move the blotting filter forward or back, release or reset the plunger, or end all processes.
"""

# Set up
import RPi.GPIO as GPIO
import time, threading
import argparse
import CSPAMpinlist as pin
import os

PWM0 = pin.pwm0  # this is the LED output pin using hardware PWMg512
os.system('gpio mode ' + str(PWM0) + ' pwm')
os.system('gpio pwmc 2')
os.system('gpio pwm-ms')


# Functions to control sensors
def powerupsensors():
    """ Turns the sensor on. """
    GPIO.output(pin.sensorpower,GPIO.HIGH)

def powerdownsensors():
    """ Turns the sensor off. """
    GPIO.output(pin.sensorpower,GPIO.LOW)


# Functions to control LED
def setLED(intensity):
    """ Sets LED percentage by convert intensity percentage to LED intensity from 0 to 1024.
    Parameter: 
        intensity: float
            The desired LED intensity percentage from 0 to 100.
    """
    intensity = int(intensity * 10.24)
    if intensity > 1024: intensity = 1024
    os.system('gpio pwm ' + str(PWM0) + ' ' + str(intensity))

def turnonLED(intensity,wait):
    """ Turns LED on to a specified intensity after a wait time. Reports when called and time when LED turns on.
    Parameters:
        intensity: float 
            The desired LED intensity percentage from 0 to 100.
        wait: float
            Seconds before the LED turns on after function is called.
    """
    print("starting turnonLED")
    time.sleep(wait)
    setLED(intensity)
    global LEDontime 
    LEDontime = time.perf_counter_ns()/(10**6) -t0
    print("turning on LED,time=",LEDontime)

def turnoffLED(wait):
    """ Turns LED off after a wait time. Reports when called and time when LED turns off.
    Parameter: 
        wait: float 
            Seconds before LED turns off after function is called. 
    """
    print("starting turnoffLED")
    time.sleep(wait)
    os.system('gpio pwm ' + str(PWM0) + ' 0')
    global LEDofftime 
    LEDofftime = time.perf_counter_ns()/(10**6) -t0
    print("turning off LED,time=",LEDofftime)


# Functions to control filter position (blotting time)
def filterforward(wait):
    """ Brings filter forward after a wait time. Reports when called and time when filter advances.
    Parameter:
        wait: float
            Seconds before filter advances after function is called.
    """
    print("starting filterforward")
    global t0
    t0 = time.perf_counter_ns()/(10**6)
    time.sleep(wait)
    GPIO.output(pin.filterposition,GPIO.HIGH)
    global filterforwardtime
    filterforwardtime = time.perf_counter_ns()/(10**6) -t0
    print("advancing the filter,time=",filterforwardtime)

def filterreverse(wait): 
    """ Reverses the filter after a wait time. Reports when called and time when filter reverses.
    Parameter:
        wait: float 
            Seconds before filter reverses after function is called. 
    """
    print("starting filterreverse")
    global t0
    t0 = time.perf_counter_ns()/(10**6)
    time.sleep(wait)
    GPIO.output(pin.filterposition,GPIO.LOW)
    global filterreversetime
    filterreversetime = time.perf_counter_ns()/(10**6) -t0
    print("reversing the filter,time=",filterreversetime)


# Functions to control plunger
def releaseplunger(wait):
    """ Releases the plunger after a wait time. Reports when called and time when plunger descends.
    Parameter:
        wait: float 
            Seconds before plunger is released after function is called.
    """
    print("starting releaseplunger")
    time.sleep(wait)
    GPIO.output(pin.plunger,GPIO.HIGH)
    global plungerreleasetime
    plungerreleasetime = time.perf_counter_ns()/(10**6) -t0
    print("releasing the plunger,time=",plungerreleasetime)

def resetplunger(wait):
    """ Resets the plunger after a wair time. Reports when called and time when plunger resets.
    Parameter:
        wait: float 
            Seconds before plunger is reset after function is called.
    """
    print("starting resetplunger")
    time.sleep(wait)
    GPIO.output(pin.plunger,GPIO.LOW)
    global resetplungertime
    resetplungertime = time.perf_counter_ns()/(10**6) -t0
    print("resetting the plunger,time=",resetplungertime)


# End processes
def endprocesses(wait):
    """ Ends C-SPAM processes by powering down the sensors, performing a GPIO cleanup and reporting the total blotting time and resolution time after a wait time. Reports when called and when finished.
    Parameter:
        wait: float 
            Seconds before end processes begins after function is called.
    """ 
    print("starting endprocesses")
    time.sleep(wait)
    powerdownsensors()
    GPIO.cleanup()
    print("Done!")
    global intendedblottingtime 
    intendedblottingtime = filterreversetime-filterforwardtime 
    print("Intended blotting time: ",intendedblottingtime)
    print("Resolution time: ", plungerreleasetime+43-LEDontime)
    print("Total blotting time: ",intendedblottingtime-applytime+t0)


# Start processes 
def applyandplungeFAST(rdelay,pdelay,ldelay,ledint):
    """ Starts the apply and plunge process after the filter has been advanced for fast millisecond resolution of samples. Reverses the filter, releases the plunger, turns on the LED, turns off the LED, resets plunger, and ends processes.
    Parameters: 
        rdelay: float 
            Seconds before retracting the filter.
        pdelay: float 
            Seconds before releasing the plunger. 
        leddelay: float
            Seconds before LED is turned on.
        ledint: float 
            Percentage of LED intensity. 
    """
    global applytime 
    applytime = time.perf_counter_ns()/(10**6)
    # Display timing and avoid crash
    print("Timings:")
    print("Filter will retract at time: ",rdelay)
    print("Plunger will fall at time: ",pdelay+rdelay)
    print("Plunger will remain energized until: ",rdelay+pdelay+ldelay+0.043+1.5)
    print("Program will exit after: ",rdelay+pdelay+ldelay+0.043+2.5)

    # Check interlock
    powerupsensors()
    if GPIO.input(pin.interlock)==1:
        print("Interlock fail: cryogen container is not in place")
        powerdownsensors()
        filterreverse(0)
        exit()
    else:
        print("Safety interlock pass: cryogen container is in place")

    # Set up processes
    plunger = threading.Thread(target=releaseplunger, args=(pdelay,))
    led = threading.Thread(target=turnonLED, args=(ledint,pdelay+ldelay))

    # Activate and run C-SPAM processes
    filterreverse(rdelay)
    plunger.start()
    led.start()
    turnoffLED(1.5+pdelay+ldelay+0.043)
    resetplunger(0)
    endprocesses(1)

def applyandplungeSLOW(rdelay,pdelay,ltime,ledint):
    """ Starts the apply and plunge process after the filter has been advanced for slower millisecond to second resolution of samples. Reverses the filter, turns on the LED, turns off the LED, releases the plunger, resets the plunger, and ends processes. 
    Parameters: 
        rdelay: float 
            Seconds before retracting the filter.     
        pdelay: float 
            Seconds before releasing the plunger. 
        ledtime: float
            Seconds LED remains on for.
        ledint: float 
            Percentage of LED intensity. 
    """
    global applytime
    applytime = time.perf_counter_ns()/(10**6)
    # Display timing and avoid crash
    print("Timings:")
    print("Filter will retract at time: ",rdelay)
    print("Light will turn on at time: ",rdelay)
    print("Light will turn off at time: ",rdelay+ltime)
    print("Plunger will fall at time: ",pdelay+ltime+rdelay)
    print("Plunger will remain energized until: ",rdelay+pdelay+ltime+0.043+1)
    print("Program will exit after: ",rdelay+pdelay+ltime+0.043+2)

    # Check interlock
    powerupsensors()
    if GPIO.input(pin.interlock)==1:
        print("Interlock fail: cryogen container is not in place")
        powerdownsensors()
        filterreverse(0)
        exit()
    else:
        print("Safety interlock pass: cryogen container is in place")

    # Activate and run C-SPAM processes
    filterreverse(rdelay)
    turnonLED(ledint,0)
    turnoffLED(ltime)
    releaseplunger(pdelay)
    resetplunger(1)
    endprocesses(1)


 
# Test code when run as main script 
if __name__=='__main__':
    # Set up
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin.cannon,GPIO.OUT)
    GPIO.setup(pin.plunger,GPIO.OUT)
    GPIO.setup(pin.filterposition,GPIO.OUT)
    GPIO.setup(pin.sensorpower,GPIO.OUT)
    GPIO.setup(pin.interlock,GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

    # Check powerupsensors 
    powerupsensors()
    if GPIO.input(pin.interlock)==1:
        print("Interlock fail: cryogen container is not in place")
        powerdownsensors(pin.sensorpower)
        filterreverse(pin.filterposition,pin.led,0)
        exit()
    else:
        print("Safety interlock pass: cryogen container is in place")

    # The following code checks the use of the rest of the functions. Functions can be run by themselves or through a thread. You can find below the code to thread all the functions, run all the functions by themselves, or only thread the plunger and LED. After testing, it was found that only threading the plunger and LED allowed for the most accurate time scale, and that code is left uncommented. The code to thread all of the functions is left commented out on top, and code to run all functions without a thread is also left commented out near the bottom for additional testing.  
#    activatefilter = threading.Thread(target=filterforward, args=(float(0),))
#    reversefilter = threading.Thread(target=filterreverse, args=(float(1),))
#    plunger = threading.Thread(target=releaseplunger, args=(float(1+0.05),))
#    ledon = threading.Thread(target=turnonLED, args=(1024,float(1+0.05+0.009),))
#    ledoff = threading.Thread(target=turnoffLED, args=(float(1+0.05+0.032+1),))
#    plungerreset = threading.Thread(target=resetplunger, args=(float(1+0.05+0.032+1),))
#    end = threading.Thread(target=endprocesses, args=(float(1+0.05+0.032+1+1),))

#    processes = [activatefilter,reversefilter,plunger,ledon,ledoff,plungerreset,end]

#    for x in processes:
#        x.start()

    filterforward(0)
    filterreverse(1)
    plunger = threading.Thread(target=releaseplunger, args=(float(1+0.05),))
    ledon = threading.Thread(target=turnonLED, args=(1024,float(1+0.05+0.014),))
    plunger.start()
    ledon.start()
#    releaseplunger(0.05)
#    turnonLED(0.01,1024)
    turnoffLED(1+1)
    resetplunger(0)
    endprocesses(1)

    
