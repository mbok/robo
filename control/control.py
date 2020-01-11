from threading import Thread
import logging
import random
import time
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt

import parts.motor as motor
import parts.pwm as pwm
import sounds as sounds
import joystick as joystick

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
  global systemRunning
  while systemRunning:
    client.publish("robo/distance", distanz(), 0, True)
    time.sleep(0.25)


def on_connect(client, userdata, flags, rc):
  print("Connected with result code " + str(rc))
  client.subscribe([("robo/motor/#", 0), ("robo/servo/#", 0), ("robo/reset", 0)])


def on_message(client, userdata, msg):
  logger.debug(msg.topic + " " + msg.payload.decode("utf-8"))
  if "motor/left/speed" in msg.topic:
    motorLeft.speed(float(msg.payload))
  elif "motor/right/speed" in msg.topic:
    motorRight.speed(float(msg.payload))
  elif "servo/arm/left/ratio" in msg.topic:
    servoArmLeft.set_ratio(float(msg.payload))
  elif "servo/arm/left/trim" in msg.topic:
    servoArmLeft.set_trim(float(msg.payload))
  elif "servo/arm/right/ratio" in msg.topic:
    servoArmRight.set_ratio(float(msg.payload))
  elif "servo/arm/right/trim" in msg.topic:
    servoArmRight.set_trim(float(msg.payload))
  elif "servo/head-h/ratio" in msg.topic:
    servoHead.set_ratio(float(msg.payload))
  elif "servo/head-h/trim" in msg.topic:
    servoHead.set_trim(float(msg.payload))
  elif "servo/head-v/ratio" in msg.topic:
    servoHeadVertical.set_ratio(float(msg.payload))
  elif "servo/head-v/trim" in msg.topic:
    servoHeadVertical.set_trim(float(msg.payload))
  elif "reset" in msg.topic:
    startup()



def startup():
  client.publish("robo/servo/arm/left/ratio", 0, 0, True)
  client.publish("robo/servo/arm/right/ratio", 0, 0, True)
  client.publish("robo/servo/head-h/ratio", 0, 0, True)
  client.publish("robo/servo/head-v/ratio", 0, 0, True)
  client.publish("robo/motor/left/speed", 0, 0, True)
  client.publish("robo/motor/right/speed", 0, 0, True)
  client.publish("robo/speach/say", "Hallo, ich bin Robi. Alle Funktionen sind hochgefahren!", 0, True)


systemRunning = True
motorLeft = motor.Motor(26, 20, pwm.PwmMotorControl(15))
motorRight = motor.Motor(13, 16, pwm.PwmMotorControl(14))
servoHeadVertical = pwm.PwmServoControl(0)
servoArmLeft = pwm.PwmServoControl(3)
servoArmRight = pwm.PwmServoControl(2)
servoHead = pwm.PwmServoControl(1)

client = mqtt.Client()
client.on_connect = on_connect
client.connect("localhost", 1883, 60)
client.on_message = on_message

client.loop_start()
soundsCtrl = sounds.SoundsControl()
soundsCtrl.start()
joystickCtrl = joystick.JoystickControl()
joystickCtrl.start()

t = Thread(target=distanceThread)
t.start()

try:
  startup()
  while True:
    time.sleep(1)
except KeyboardInterrupt:
  print("W: interrupt received, stopping")
finally:
  systemRunning = False
  motorLeft.stop()
  motorRight.stop()
  soundsCtrl.stop()
  joystickCtrl.stop()
  client.loop_stop()
  raise SystemExit
