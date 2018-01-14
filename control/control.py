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
  client.subscribe("robo/#")

def on_message(client, userdata, msg):
  print(msg.topic + " " + str(msg.payload))
  if "motor/left/speed" in msg.topic:
    motorLeft.speed(float(msg.payload))
  elif "motor/right/speed" in msg.topic:
    motorRight.speed(float(msg.payload))

pwm = pwm.PwmControl()
motorLeft = motor.Motor(26, 20, pwm, 15)
motorRight = motor.Motor(19, 16, pwm, 14)

client = mqtt.Client()
client.on_connect = on_connect
client.connect("master", 1883, 60)
client.on_message = on_message
client.loop_start()

i = 0
while i < 100:
  time.sleep(1)
  i += 1

motorLeft.stop()
motorRight.stop()
client.loop_stop()