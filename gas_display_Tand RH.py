#!/usr/bin/env python3
########################################################################
# Filename    : I2CLCD1602.py
# Description : Use the LCD display data
# Author      : freenove
# modification: 2018/08/03
########################################################################
from PCF8574 import PCF8574_GPIO
from Adafruit_LCD1602 import Adafruit_CharLCD
import time
import RPi.GPIO as GPIO
import Freenove_DHT as DHT
DHTPin = 11     #define the pin of DHT11
from time import sleep, strftime
from datetime import datetime
from ADCDevice import *

adc = ADCDevice() # Define an ADCDevice class object

def setup():
    global adc
    if(adc.detectI2C(0x48)): # Detect the pcf8591.
        adc = PCF8591()
    elif(adc.detectI2C(0x4b)): # Detect the ads7830
        adc = ADS7830()
    else:
        print("No correct I2C address found, \n"
        "Please use command 'i2cdetect -y 1' to check the I2C address! \n"
        "Program Exit. \n");
        exit(-1)

def get_cpu_temp():     # get CPU temperature from file "/sys/class/thermal/thermal_zone0/temp"
    tmp = open('/sys/class/thermal/thermal_zone0/temp')
    cpu = tmp.read()
    tmp.close()
    return '{:.2f}'.format( float(cpu)/1000 ) + ' C'

def get_time_now():     # get system time
    return datetime.now().strftime('    %H:%M:%S')

def loop():
    mcp.output(3,1)     # turn on LCD backlight
    lcd.begin(16,2)     # set number of LCD lines and columns
    while(True):
        #lcd.clear()
        dht = DHT.DHT(DHTPin)   #
        RH = dht.humidity
        TEMP = dht.temperature
        value = adc.analogRead(0)    # read the ADC value of channel 0
        voltage = value / 255.0 * 5.0  # calculate the voltage value
        R2=1000;
        #Activate line 31 to 33 and line 40 for re-calibration of the sensor for environment or sensor changes
        #RS_gas_T = ((5.0*R2)/voltage)-R2;
        #R0=RS_gas_T/60;

        #print ('ADC Value : %d, Concentration : %.2f mg/L, i.e.%.2f ppm'%(value,R0,R0/0.00188))
        R0=120.43;# get it from a calibration in clean-air environment, 24.7C, 30~50%RH, FC-22 sensor
        RS_gas=((5.0*R2)/voltage)-R2;
        ratio=RS_gas/R0;
        ratio_T=ratio-0.004*(TEMP-20) # temp. reference of MQ-3 google drive is 20C
        ratio_RH=ratio_T-0.1/52*(RH-33) # RH. reference is 33 % to 85%
        x=0.4*ratio_RH;
        concentration = pow(x,-1.431);
        print ('ADC Value : %d, Concentration : %.2f mg/L, i.e.%.2f ppm'%(value,concentration,concentration/0.00188))


        lcd.setCursor(0,0)  # set cursor position
        lcd.message('Ethanol:'+ str('%.2fmg/L' %(concentration)) +'\n' )# display CPU temperature
        lcd.message( 'in ppm:'+ str('%.4f' %(concentration/0.00188)) )   # display the time
        sleep(3)
        lcd.setCursor(0,0)  # set cursor position
        lcd.message('CPU Temp:'+ get_cpu_temp() +'\n' )# display CPU temperature
        lcd.message( get_time_now()+'   ' )   # display the time
        sleep(3)

def destroy():
    lcd.clear()
    abc.close()
    GPIO.cleanup()

PCF8574_address = 0x27  # I2C address of the PCF8574 chip.
PCF8574A_address = 0x3F  # I2C address of the PCF8574A chip.
# Create PCF8574 GPIO adapter.
try:
    mcp = PCF8574_GPIO(PCF8574_address)
except:
    try:
        mcp = PCF8574_GPIO(PCF8574A_address)
    except:
        print ('I2C Address Error !')
        exit(1)
# Create LCD, passing in MCP GPIO adapter.
lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=mcp)

if __name__ == '__main__':
    print ('Program is starting ... ')
    try:
        setup()
        loop()
    except KeyboardInterrupt:
        destroy()