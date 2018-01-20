import time
import logging
import paho.mqtt.client as mqtt
import parts.motor as motor
import parts.pwm as pwm
import RPi.GPIO as GPIO
import random
from threading import Thread

GPIO.setmode(GPIO.BCM)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("control")

def dynamicServos():
  if dynamicServosEnabled:
    client.publish("robo/servo/arm/left/ratio", (-100 + random.random() * 200), 0, True)
    client.publish("robo/servo/body/ratio", (-100 + random.random() * 200), 0, True)
    client.publish("robo/servo/head/ratio", (-100 + random.random() * 200), 0, True)
    time.sleep(random.random() * 2.0)


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
  elif "servo/dynamic" in msg.topic:
    if (int(msg.payload) == 1):
      dynamicServosEnabled = True
    elif (int(msg.payload) == 0):
      dynamicServosEnabled = False

dynamicServosEnabled = False
t = Thread(target=dynamicServos)
t.start()
motorLeft = motor.Motor(26, 20, pwm.PwmMotorControl(15))
motorRight = motor.Motor(19, 16, pwm.PwmMotorControl(14))
servoArmLeft = pwm.PwmServoControl(3)
servoBody = pwm.PwmServoControl(1)
servoHead = pwm.PwmServoControl(2)

client = mqtt.Client()
client.on_connect = on_connect
client.connect("master", 1883, 60)
client.on_message = on_message

try:
  client.loop_forever()
except KeyboardInterrupt:
  print("W: interrupt received, stopping")
finally:
  motorLeft.stop()
  motorRight.stop()
