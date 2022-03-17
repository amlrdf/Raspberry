#!/usr/bin/env python3
########################################################################
# Filename    : ADC.py
# Description : Use ADC module to read the voltage value of potentiometer.
# Author      : www.freenove.com
# modification: 2020/03/06
########################################################################
import time
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

def loop():
    while True:
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
        x=0.4*ratio;
        concentration = pow(x,-1.431);
        print ('ADC Value : %d, Concentration : %.2f mg/L, i.e.%.2f ppm'%(value,concentration,concentration/0.00188))
        time.sleep(0.1)

def destroy():
    adc.close()

if __name__ == '__main__':   # Program entrance
    print ('Program is starting ... ')
    try:
        setup()
        loop()
    except KeyboardInterrupt: # Press ctrl-c to end the program.
        destroy()