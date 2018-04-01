from threading import Thread
from gtts import gTTS

import logging
import random
import time
import hashlib
import os.path

import pygame as pg

import urllib

import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt

import parts.motor as motor
import parts.pwm as pwm
import sounds as sounds

GPIO.setmode(GPIO.BCM)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("control")
GPIO_TRIGGER = 23
GPIO_ECHO = 24
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

# Init music
freq = 44100    # audio CD quality
bitsize = -16   # unsigned 16 bit
channels = 2    # 1 is mono, 2 is stereo
buffer = 2048   # number of samples (experiment to get right sound)
pg.mixer.init(freq, bitsize, channels, buffer)
pg.mixer.music.set_volume(1)


def play_music(music_file, wait=True):
  clock = pg.time.Clock()
  if pg.mixer.music.get_busy():
    pg.mixer.music.fadeout(1000)
    pg.mixer.music.stop()
  try:
    pg.mixer.music.load(music_file)
    print("Music file {} loaded!".format(music_file))
  except pygame.error:
    print("File {} not found! {}".format(music_file, pg.get_error()))
    return

  pg.mixer.music.play()

  # If you want to fade in the audio...
  # for x in range(0,100):
  #     pg.mixer.music.set_volume(float(x)/100.0)
  #     time.sleep(.0075)
  # # check if playback has finished
  if (wait):
    while pg.mixer.music.get_busy():
      clock.tick(30)


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
  client.subscribe([("robo/motor", 0), ("robo/servo", 0)])


def on_message(client, userdata, msg):
  global speachLanguage
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
  elif "speach/say" in msg.topic:
    text = msg.payload.decode("utf-8")
    textHash = speachLanguage + "-" + hashlib.md5(text.encode("utf-8")).hexdigest()
    file = "/tmp/speach+"+str(textHash)+".mp3"
    logger.debug("File for speach: " + file)
    if not os.path.isfile(file):
      logger.debug("Downloading speach to: " + file)
      tts = gTTS(text=text, lang=speachLanguage, slow=True)
      tts.save(file)
    play_music(file, False)
  elif "speach/lang" in msg.topic:
    speachLanguage = str(msg.payload)
  elif "music/play/file" in msg.topic:
    file = str(msg.payload)
    if os.path.isfile(file):
      play_music(file, False)
    else:
      logger.warn("File not found: " + file)
  elif "music/stop" in msg.topic:
    pg.mixer.music.stop()
  elif "sounds/play/url" in msg.topic:
    url = str(msg.payload)
    soundHash = hashlib.md5(url.encode()).hexdigest()
    file = "/tmp/sound+"+str(soundHash)+".wav"
    logger.debug("File for sound: " + file)
    if not os.path.isfile(file):
      logger.debug("Downloading sound to: " + file)
      urllib.urlretrieve(url, file)
    sound = pg.mixer.Sound(file)
    sound.play()
  elif "sounds/stop" in msg.topic:
    pg.mixer.stop()
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
speachLanguage = "de"
speachCount = 0
motorLeft = motor.Motor(26, 20, pwm.PwmMotorControl(15))
motorRight = motor.Motor(13, 16, pwm.PwmMotorControl(14))
servoHeadVertical = pwm.PwmServoControl(0)
servoArmLeft = pwm.PwmServoControl(3)
servoArmRight = pwm.PwmServoControl(2)
servoHead = pwm.PwmServoControl(1)

client = mqtt.Client()
client.on_connect = on_connect
client.connect("master", 1883, 60)
client.on_message = on_message

soundsCtrl = sounds.SoundsControl()
soundsCtrl.start()

t = Thread(target=distanceThread)
t.start()

try:
  startup()
  client.loop_forever()
except KeyboardInterrupt:
  print("W: interrupt received, stopping")
finally:
  systemRunning = False
  motorLeft.stop()
  motorRight.stop()
  soundsCtrl.stop()
  raise SystemExit
