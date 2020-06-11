import os
import time
import datetime
import glob
import MySQLdb
import time
import requests

import Adafruit_DHT as ada
import RPi.GPIO as GPIO


sensor = ada.DHT11
GPIO.setmode(GPIO.BOARD)
motor = 3
GPIO.setup(motor,GPIO.OUT)

gpio = 17

domainName = "http://water-garden.herokuapp.com"


#temp_sensor ='/home/pi/Desktop/test.txt'
db = MySQLdb.connect(host="localhost",user="root",passwd="123", db="pi")
cur = db.cursor()

currentState = False;
def saveToDb(humility, temperature, isSent):
    sql = ("""INSERT INTO SENSOR_VALUE(humility, temprerature, is_sent) VALUES (%f,%f, %r)""" %(temperature, humility, isSent))
    print(sql)
    try:
	print "writing to database..."
	cur.execute(sql)
	print("exceuted")
	db.commit()
	print "write to DB thanh cong"
    except:
	db.rollback()
	print "false"



while True:
        humility, temperature = ada.read_retry(sensor,gpio)
        isSent = True
        # try to post data
        postTemperature = requests.post(domainName + "/api/sensor-value/26/new", json={'value': temperature })
        postHumility = requests.post(domainName + "/api/sensor-value/25/new", json={'value': humility })
        if (postTemperature.status_code != 200 or postHumility.status_code != 200): # get errors
            isSent = False
            # If cant send, save data to Db
            print(postTemperature.status_code)
            
            saveToDb(humility, temperature, isSent)
        else:
            print ("sent to Web service\n")       
	
            
	getStateOfSensor = requests.get(domainName + "/api/device/13/state")
        print(getStateOfSensor.json())
	if (getStateOfSensor.json() == True):
            print("Bat")
            #if(currentState != True):
            GPIO.output(motor,GPIO.HIGH)
            
        else:
            print("Tat")
            #GPIO.output(channel,(GPIO.LOW,GPIO.HIGH))
            #if currentState == True:
            GPIO.output(motor,GPIO.LOW)
            #GPIO.cleanup()
	# send or save to DB every 10s
        #time.sleep(10)
cur.close()
db.close()
GPIO.cleanup()
#break
