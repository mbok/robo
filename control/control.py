import time
import logging
import paho.mqtt.client as mqtt
import parts.motor as motor
import parts.pwm as pwm
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
logging.basicConfig(level=logging.DEBUG)


def on_connect(client, userdata, flags, rc):
  print("Connected with result code " + str(rc))

# client = mqtt.Client()
# client.on_connect = on_connect

# client.connect("localhost", 1883, 60)

# client.loop_start()

pwm = pwm.PwmControl()
motorLeft = motor.Motor(26, 20, pwm, 15)

i = 0
while i < 100:
  motorLeft.forward(i / 100.0)
  time.sleep(1)
  i += 1

motorLeft.stop()
#  client.publish("test/temperature", "test")