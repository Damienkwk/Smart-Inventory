import thread, threading
# Imports for flask
from flask import Flask

# Setup for flask
app = Flask(__name__)

# Imports for LCD
import I2C_LCD_driver
from time import *

# Imports for Load Cell
import RPi.GPIO as GPIO
import time
import sys
from hx711 import HX711

# Set up for loadcell
hx = HX711(5, 6)
hx.set_reading_format("LSB", "MSB")
hx.set_reference_unit(427)
hx.reset()
hx.tare(times=30)

# Set up for LCD
mylcd = I2C_LCD_driver.lcd()

# Set up some global variables
val=0
import ast
GPIO.setup(17,GPIO.OUT)
GPIO.setup(27,GPIO.OUT)


# Set up functions for printing to LCD
def updateLCD(LCDLine1,LCDLine2=""):
    mylcd.lcd_clear()
    """Prints l1 one top row and l2 on second row of LCD"""
    mylcd.lcd_display_string(str(LCDLine1), 1)
    mylcd.lcd_display_string(str(LCDLine2), 2)


def lprint(toPrint,row=2,x=3):
    """Prints value at given row and column. Default is row 2, column 4 (starts at 0)"""
    mylcd.lcd_display_string(str(toPrint), row, x)


# Set up for buttons
prev_input_t = 1
prev_input_w = 1
pin_t=20
pin_w=21
GPIO.setup(pin_t, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(pin_w, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


showValue=True

@app.route('/setTare')
def setTare():
    global showValue
    """Tares the scale while printing to lcd"""
    showValue=False
    delay(0.5)
    updateLCD("TARING...")
    hx.tare(times=20)
    delay(0.5)
    updateLCD("Done ...")
    showValue=True
    delay(0.5)
    return 'Done...'


@app.route('/getVal')
def getVal():
    global val
    return str(val)+"g"


def cleanAndExit():
    """"To clean GPIO pins before exiting program"""
    updateLCD("Cleaning...")
    GPIO.cleanup()
    delay(3)
    updateLCD("Goodbye!")
    #sys.exit()


def readValue(times=15, update=True):
    global val
    val = hx.get_weight(times)
    if update:
        updateLCD(val)
    hx.power_down()
    hx.power_up()
    return val


def delay(secs):
    """Used to allow reading of lcd; secs should be a int or float"""
    time.sleep(secs)


def guessNoItems(Tw,w):
    print Tw,float(Tw),int(Tw)
    print w,float(w),int(w)
    return float(Tw)/float(w)


@app.route('/count=<obj>')
def countItems(obj):
    global showValue
    showValue=False
    obj = ast.literal_eval(obj)
    name=obj.get("item")
    weight=obj.get("weight")
    weight=weight[:-1]
    updateLCD("Weighing..     ")
    totalWeight=readValue(update=False)
    lprint(totalWeight,row=2, x=0)
    lprint("Counting    ",row=1, x=0)
    lprint("            ",row=2, x=0)
    noOfItems = guessNoItems(totalWeight,weight)
    lprint("Results    ",row=1, x=0)
    if float(noOfItems)%1 != 0:
        noOfItems="Unknown"
    else:
        if int(noOfItems)<3:
            light("red")
        else:
            light("green")
    lprint(str(noOfItems)+" "+name+"(s)")
    showValue=True
    return str(noOfItems)

@app.route('/red')
def lightRed():
    print "red"
    GPIO.output(17,GPIO.HIGH)
    time.sleep(5)
    GPIO.output(17,GPIO.LOW)
    return "a"

@app.route('/green')
def lightGreen():
    print "green"
    GPIO.output(27,GPIO.HIGH)
    time.sleep(5)
    GPIO.output(27,GPIO.LOW)
    return "b"


def light(col):
    print "in light"
    if col=="red":
        try:
            thread.start_new_thread(lightRed,())
        except:
            print "Error: unable to start thread:",sys.exc_info()[0]
    elif col=="green":
        try:
            thread.start_new_thread(lightGreen,())
        except:
            print "Error: unable to start thread:",sys.exc_info()[0]


def handle_t(pin):
    try:
        global showValue
        showValue=False
        setTare()
    except RuntimeError:
        pass


updateLCD("Welcome!")

GPIO.add_event_detect(pin_t, GPIO.RISING, callback=handle_t, bouncetime=200)
delay(3)


def printVal():
    while True:
        try:
            while(showValue):
                readValue()
        except (KeyboardInterrupt, SystemExit, RuntimeError):
            cleanAndExit()

try:
    thread.start_new_thread(printVal,())
except:
    print "Error: unable to start thread:",sys.exc_info()[0]



import signal


import sys

def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    cleanAndExit()
    threads = threading.enumerate()
    print "Sending kill to threads..."
    for t in threads:
        if t is not None and t.isAlive():
            t.kill_received = True
    updateLCD("           ")
    sys.exit(0)



signal.signal(signal.SIGINT, signal_handler)

# check purpose of this
#signal.pause()



app.run(host='0.0.0.0', port=4000)
