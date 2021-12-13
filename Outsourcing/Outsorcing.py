import RPi.GPIO as GPIO
import lcddriver
import requests
import socket
import spidev
import time
display = lcddriver.lcd()
GPIO.setwarnings(False)
count = 0 
def Bluetooth():
	hostMACAddress = 'b8:27:eb:84:0b:38'
	port = 1 
	backlog = 1
	size = 1024
	s=socket.socket(socket.AF_BLUETOOTH,socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
	s.bind((hostMACAddress,port))
	s.listen(backlog)
	client, address = s.accept()
        msg = client.recv(size)
	print (format(msg))
	return format(msg) 
def LCD():
        display.lcd_display_string("      502       ", 1)
       	display.lcd_display_string("  GAS WARNING!  ", 2)
	time.sleep(2)
def Gas_Sensor():
	spi = spidev.SpiDev()
	spi.open(0,0)
	spi.max_speed_hz=1350000 
	channel = 0
        buff = spi.xfer2([1,8+channel<<4,0])
       	data = ((buff[1]&3)<<8)+buff[2]
       	return data
def Message():
	if Gas_Sensor() > 200:
		requests.post('https://maker.ifttt.com/trigger/gas/with/key/dyY3vEB3txNzyPOOmoZjGJ')


def Servo_Motor():
	PIN1 = 18 
	Angle = 5 
	GPIO.setmode(GPIO.BCM) 
	GPIO.setup(PIN1,GPIO.OUT) 
	SERVO = GPIO.PWM(PIN1, 50) 
	SERVO.start(0) 
	if Gas_Sensor() > 200: 
        	if Angle == 5: 
               		SERVO.ChangeDutyCycle(Angle) 
			time.sleep(0.1)
                	Angle += 5
	else:
		SERVO.ChangeDutyCycle(10)
		time.sleep(0.1)
def LED(): 
	PIN = 21 
	GPIO.setmode(GPIO.BCM) 
	GPIO.setup(PIN,GPIO.OUT) 
	if Gas_Sensor() > 200:
		GPIO.output(PIN,GPIO.HIGH)
	else: 
		GPIO.output(PIN,GPIO.LOW)
def DC_Motor():
	PIN1 = 23
    PIN2 = 24
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(PIN1,GPIO.OUT) 
	GPIO.setup(PIN2,GPIO.OUT)
	if Gas_Sensor() > 200:
		GPIO.output(PIN1,GPIO.LOW) 
		GPIO.output(PIN2,GPIO.HIGH)
		time.sleep(0.1)
	else:
		GPIO.output(PIN1,GPIO.LOW) 
		GPIO.output(PIN2,GPIO.LOW)
		is_running=False
try:
	while(True): 
		print(Gas_Sensor())
		time.sleep(1) 
		count
		if Gas_Sensor() > 200: 
			if count == 0: 
				Message() 
				count += 1 
			LED() 
			DC_Motor() 
			Servo_Motor() 
			if count == 1: 
				if Bluetooth() =='1':  
					LCD() 
					count +=1
		else:
			count = 0 
			LED()
			Servo_Motor()
			DC_Motor()
			GPIO.cleanup() 
			display.lcd_clear()
        	is_running=False
except KeyboardInterrupt:
        GPIO.cleanup()
	    is_running=False
	    display.lcd_clear()
