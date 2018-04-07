import logging

import paho.mqtt.client as mqtt

class JoystickControl:
  def __init__(self):
    self.logger = logging.getLogger("joystick")

    self.client = mqtt.Client()
    self.client.on_connect = self.on_connect
    self.client.connect("master", 1883, 60)
    self.client.on_message = self.on_message
    self.h_ratio = 0.0
    self.v_ratio = 0.0

  def on_connect(self, client, userdata, flags, rc):
    self.logger.info("Connected joystick with result code " + str(rc))
    client.subscribe(
        [("robo/joystick/#", 0), ("robo/reset", 0)])

  def on_message(self, client, userdata, msg):
    self.logger.debug(msg.topic + " " + msg.payload.decode("utf-8"))
    if "joystick/h/ratio" in msg.topic:
      self.h_ratio = float(msg.payload)
      self.update()
    elif "joystick/v/ratio" in msg.topic:
      self.v_ratio = float(msg.payload)
      self.update()
    elif "reset" in msg.topic:
      self.h_ratio = 0.0
      self.v_ratio = 0.0
      self.update()

  def update(self):
    h = self.h_ratio / 100
    v = self.v_ratio / 100
    if h > 0:
      left = 1
      right = -2 * h + 1
    else:
      left = 2 * h + 1
      right = 1
    left *= v
    right *= v
    self.client.publish("robo/motor/left/speed", left * 100, 0, True)
    self.client.publish("robo/motor/right/speed", right * 100, 0, True)

  def start(self):
    self.client.loop_start()

  def stop(self):
    self.client.loop_stop(True)