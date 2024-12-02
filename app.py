from math import prod
import time, sys
from typing import OrderedDict
from flask import Flask, render_template, request
import csv
from datetime import datetime

app = Flask(__name__) 
oven = {
    "ovenRunning": False,
    "orderID": "0",
    "timeLeft": 0, # seconds
    "queue": []
}
ordersList = []
currentOrder = []
products = []
lastOrderNumber = 0

def fill_products():
    with open('products.csv') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        for row in csv_reader:
            products.append(row)

# Homepage
@app.route("/") 
def index():
    return render_template('index.html')

# Restaurant menu (chosing products)
@app.route("/menu")
def menu():
    global products
    return render_template('menu.html', products = products)

# Accept order
@app.route("/add_order", methods=['POST'])
def add_order():
    global lastOrderNumber
    newOrder = request.json # 0: ordered products
    orderNumber = lastOrderNumber + 1
    # 1: name, 2: phone, 3: time_preference, 4: message
    newOrder.append(orderNumber) # 5: order ID
    newOrder.append("notDone") # 6: order status
    newOrder.append(time.time()) # 7: timestamp
    lastOrderNumber = orderNumber
    ordersList.append(newOrder)
    print(ordersList)
    return "OK", 200

# Checkout page
@app.route("/checkout")
def checkout():
    return render_template('detail.html')

# Smart oven
@app.route("/oven", methods=['GET', 'POST']) 
def oven_update():
    global oven, currentOrder
    if currentOrder == []:
        oven["ovenRunning"] = False
        oven["orderID"] = "0"
        oven["timeLeft"] = 0
    else:
        oven["ovenRunning"] = True
        oven["orderID"] = currentOrder[5]
        firstItem = True
        for x in currentOrder[0]:
            if x["dish"] == "pizza":
                if firstItem:
                    oven["timeLeft"] = int(x["cooktime"])
                    firstItem = False
                else:
                    oven["queue"].append(int(x["cooktime"]))

    if request.method == 'POST':
        oven = request.json
        if not oven["ovenRunning"]:
            currentOrder = []
        return "OK", 200
    else:
        return oven

# Kitchen display
@app.route("/kitchen")
def kitchen():
    global ordersList, time, datetime
    return render_template('kitchen.html', ordersList = ordersList, time = time, int = int, datetime = datetime)

# Thanks page
@app.route("/thanks")
def thanks():
    return render_template('thanks.html')

# Set current order
@app.route("/current_order", methods=['GET', 'POST'])
def current_order():
    global currentOrder
    if request.method == 'POST':
        ordersList[request.json][6] = "inProgress"
        currentOrder = ordersList[request.json]
        print(currentOrder)
        return "OK", 200
    else:
        return currentOrder

# Cashier page for Restaurant
@app.route("/cashier")
def cashier():
    global products
    return render_template('order.html', products = products)

# Change order status to "done"
@app.route("/finish_order", methods=['POST'])
def finish_order():
    global currentOrder, ordersList
    print(currentOrder)
    ordersList[request.json][6] = "done"
    currentOrder = []
    return "OK", 200

# Timing check
@app.route("/queue_time")
def available_times():
    global ordersList
    orderCount = 0
    totalWaitingTime = 0
    for x in ordersList:
        if x[6] == "notDone" or x[6] == "inProgress":
            orderCount += 1
            for y in x[0]:
                totalWaitingTime += float(y["cooktime"])
    return [orderCount, totalWaitingTime]

if __name__ == "__main__":
    fill_products()
    app.run(debug=True, use_reloader=False, host='0.0.0.0')