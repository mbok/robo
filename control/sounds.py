import hashlib
import logging
import os.path
import urllib
#import urllib.request
import re

import paho.mqtt.client as mqtt
import pygame as pg
from gtts import gTTS

# Init music
freq = 44100    # audio CD quality
bitsize = -16   # unsigned 16 bit
channels = 2    # 1 is mono, 2 is stereo
buffer = 2048   # number of samples (experiment to get right sound)
pg.mixer.init(freq, bitsize, channels, buffer)
pg.mixer.music.set_volume(1)

class SoundsControl:
  def __init__(self):
    self.logger = logging.getLogger("sounds")
    self.client = mqtt.Client()
    self.client.on_connect = self.on_connect
    self.client.connect("master", 1883, 60)
    self.client.on_message = self.on_message
    self.speachLanguage = "de"

  def on_connect(self, client, userdata, flags, rc):
    self.logger.info("Connected sounds with result code " + str(rc))
    client.subscribe(
        [("robo/speach/#", 0), ("robo/music/#", 0), ("robo/sounds/#", 0)])

  def on_message(self, client, userdata, msg):
    self.logger.debug(msg.topic + " " + msg.payload.decode("utf-8"))
    if "speach/say" in msg.topic:
      text = msg.payload.decode("utf-8")
      textHash = self.speachLanguage + "-" + hashlib.md5(
        text.encode("utf-8")).hexdigest()
      file = "/tmp/speach+" + str(textHash) + ".mp3"
      self.logger.debug("File for speach: " + file)
      if not os.path.isfile(file):
        self.logger.debug("Downloading speach to: " + file)
        tts = gTTS(text=text, lang=self.speachLanguage, slow=True)
        tts.save(file)
        self.logger.debug("Speach downloaded to: " + file)
      self.play_music(file, False)
    elif "speach/lang" in msg.topic:
      self.speachLanguage = str(msg.payload)
    elif "music/play/file" in msg.topic:
      file = str(msg.payload)
      if os.path.isfile(file):
        self.play_music(file, False)
      else:
        self.logger.warn("File not found: " + file)
    elif "music/stop" in msg.topic:
      pg.mixer.music.stop()
    elif "sounds/play/url" in msg.topic:
      url = msg.payload.decode("utf-8")
      self.logger.debug("Going to play sound: " + url)
      soundHash = hashlib.md5(url.encode()).hexdigest()
      file = "/tmp/sound+" + str(soundHash) + ".wav"
      self.logger.debug("File for sound: " + file)
      if not os.path.isfile(file):
        self.logger.debug("Downloading sound " + url + " to: " + file)
        urllib.urlretrieve(url, file)
        self.logger.debug("Downloaded sound to: " + file)
      sound = pg.mixer.Sound(file)
      m = re.match(r".*sounds/play/url/(\d+)", msg.topic)
      if m:
        channel = pg.mixer.Channel(int(m.group(1)))
        channel.play(sound, -1)
      else:
        sound.play(-1)
    elif "sounds/stop" in msg.topic:
      m = re.match(r".*sounds/stop/(\d+)", msg.topic)
      if m:
        channel = pg.mixer.Channel(int(m.group(1)))
        channel.stop()
      else:
        pg.mixer.stop()

  def start(self):
    self.client.loop_start()

  def stop(self):
    self.client.loop_stop(True)

  def play_music(self, music_file, wait=True):
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
