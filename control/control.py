import logging
import random
import time
from threading import Thread

import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt

import parts.motor as motor
import parts.pwm as pwm

GPIO.setmode(GPIO.BCM)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("control")
GPIO_TRIGGER = 23
GPIO_ECHO = 24
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)


def distanz():
  # setze Trigger auf HIGH
  GPIO.output(GPIO_TRIGGER, True)

  # setze Trigger nach 0.01ms aus LOW
  time.sleep(0.00001)
  GPIO.output(GPIO_TRIGGER, False)

  StartZeit = time.time()
  StopZeit = time.time()

  # speichere Startzeit
  while GPIO.input(GPIO_ECHO) == 0:
    StartZeit = time.time()

  # speichere Ankunftszeit
  while GPIO.input(GPIO_ECHO) == 1:
    StopZeit = time.time()

  # Zeit Differenz zwischen Start und Ankunft
  TimeElapsed = StopZeit - StartZeit
  # mit der Schallgeschwindigkeit (34300 cm/s) multiplizieren
  # und durch 2 teilen, da hin und zurueck
  distanz = (TimeElapsed * 34300) / 2

  return distanz


def distanceThread():
  while True:
    client.publish("robo/distance", distanz(), 0, True)
    time.sleep(0.25)


def on_connect(client, userdata, flags, rc):
  print("Connected with result code " + str(rc))
  client.subscribe("robo/#")


def on_message(client, userdata, msg):
  logger.debug(msg.topic + " " + str(msg.payload))
  if "motor/left/speed" in msg.topic:
    motorLeft.speed(float(msg.payload))
  elif "motor/right/speed" in msg.topic:
    motorRight.speed(float(msg.payload))
  elif "servo/arm/left/ratio" in msg.topic:
    servoArmLeft.set_ratio(float(msg.payload))
  elif "servo/arm/left/trim" in msg.topic:
    servoArmLeft.set_trim(float(msg.payload))
  elif "servo/body/ratio" in msg.topic:
    servoBody.set_ratio(float(msg.payload))
  elif "servo/body/trim" in msg.topic:
    servoBody.set_trim(float(msg.payload))
  elif "servo/head/ratio" in msg.topic:
    servoHead.set_ratio(float(msg.payload))
  elif "servo/head/trim" in msg.topic:
    servoHead.set_trim(float(msg.payload))


motorLeft = motor.Motor(26, 20, pwm.PwmMotorControl(15))
motorRight = motor.Motor(19, 16, pwm.PwmMotorControl(14))
servoArmLeft = pwm.PwmServoControl(3)
servoBody = pwm.PwmServoControl(1)
servoHead = pwm.PwmServoControl(2)

client = mqtt.Client()
client.on_connect = on_connect
client.connect("master", 1883, 60)
client.on_message = on_message

t = Thread(target=distanceThread)
t.start()

try:
  client.loop_forever()
except KeyboardInterrupt:
  print("W: interrupt received, stopping")
finally:
  motorLeft.stop()
  motorRight.stop()
