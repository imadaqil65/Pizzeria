from fhict_cb_01.CustomPymata4 import CustomPymata4
import time, sys
from flask import Flask, render_template
import requests
from datetime import datetime

timestamp = time.time()
app = Flask(__name__) 
localOven = {}
currentOrder = ""
button1State = 0
button2State = 0

def button1_call(data):
    global button1State
    button1State = data[2]

def button2_call(data):
    global button2State
    button2State = data[2]

def setup():
    global board, localOven, button1State, button2State
    # Windows dynamic port workaround
    portnum = 0
    while True:
        if 'board' not in globals() and portnum < 15:
            try:
                board = CustomPymata4(com_port = f"COM{portnum}")
            except:
                portnum += 1
        else:
            break
    # I/O declarations
    board.set_pin_mode_digital_output(4) # LED 1
    board.set_pin_mode_digital_output(5) # LED 2
    board.set_pin_mode_digital_output(6) # LED 3
    board.set_pin_mode_digital_output(7) # LED 4
    board.displayOn()
    board.set_pin_mode_digital_input_pullup(8, callback = button1_call) # button 1
    board.set_pin_mode_digital_input_pullup(9, callback = button2_call) # button 2
    # localOven needs to have initial data
    localOven = requests.get("http://127.0.0.1:5000/oven").json()

def loop():
    global timestamp, localOven, currentOrder, prevButton1State, prevButton2State
    if (not localOven["ovenRunning"] and time.time() - timestamp > 5):
        localOven = requests.get("http://127.0.0.1:5000/oven").json()
        timestamp = time.time()
    if currentOrder != localOven["orderID"]:
        currentOrder = localOven["orderID"]
        board.displayShow(currentOrder)
        while True:
            # start new order on button 1 press
            if button1State != 1:    
                break
    if localOven["ovenRunning"]:
        board.digital_pin_write(4, 1) # red on
        board.digital_pin_write(5, 0) # green off
        board.digital_pin_write(7, 0) # yellow off
        board.displayShow(localOven["timeLeft"])
        oven_timer()
    else:
        board.displayShow("----")
        board.digital_pin_write(4, 0) # red off
        board.digital_pin_write(5, 1) # green on
        board.digital_pin_write(7, 0) # yellow off
    time.sleep(0.01) # Give Firmata some time to handle protocol.

def oven_timer():
    global button1State
    time.sleep(1)
    if localOven["timeLeft"] > 0:
        localOven["timeLeft"] -= 1
    elif localOven["queue"] != []:
        localOven["timeLeft"] = localOven["queue"].pop(0)
        board.displayShow("Strt")
        board.digital_pin_write(4, 0) # red off
        board.digital_pin_write(7, 1) # yellow on
        while True:
            # start new order on button 1 press
            if button1State != 1:    
                break
    else:
        localOven["ovenRunning"] = False
    requests.post("http://127.0.0.1:5000/oven", json=localOven)

#--------------
# main program
#--------------
setup()
while True:
    try:
        loop()
    except KeyboardInterrupt: # crtl+C
        print ('shutdown')
        board.shutdown()
        sys.exit(0)  