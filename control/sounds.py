import paho.mqtt.client as mqtt
import logging

class SoundsControl:
  def __init__(self):
    self.logger = logging.getLogger("sounds")
    self.client = mqtt.Client()
    self.client.on_connect = self.on_connect
    self.client.connect("master", 1883, 60)
    self.client.on_message = self.on_message

  def on_connect(self, client, userdata, flags, rc):
    print("Connected sounds with result code " + str(rc))
    client.subscribe([("robo/speach",0), ("robo/music",0), ("robo/sounds",0)])

  def on_message(self, client, userdata, msg):
    self.logger.debug(msg.topic + " " + msg.payload.decode("utf-8"))

  def start(self):
    self.client.loop_start()

  def stop(self):
    self.client.loop_stop(True)
