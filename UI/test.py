from flask import Flask, jsonify
from random import *
import time
import json

app = Flask(__name__)


@app.route('/getVal')
def getWeight():
    weight = randint(1, 100)
    return (str(weight)+"g")



@app.route('/setTare')
def setTare():
    time.sleep(5)
    return ""

@app.route('/count')
def count():
    return 2

@app.route('/onCount=<data>')
def onCount(data):
    print(data)
    return ""


app.run(host='0.0.0.0', port=4000)