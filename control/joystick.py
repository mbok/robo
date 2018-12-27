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
    payload = msg.payload.decode("utf-8")
    if "joystick/h/ratio" in msg.topic:
      self.h_ratio = float(payload)
      self.update2()
    elif "joystick/v/ratio" in msg.topic:
      self.v_ratio = float(payload)
      self.update2()
    elif "joystick/hxv/ratio" in msg.topic:
      self.logger.debug("Joystick hxv update")
      ratios = str(payload).split("x")
      self.h_ratio = float(ratios[0])
      self.v_ratio = float(ratios[1])
      self.logger.debug("beide motoren ein")
      self.update2()
    elif "reset" in msg.topic:
      self.reset()

  def update2(self):
    self.logger.debug("Start updating motors")
    h = self.h_ratio / 100
    v = self.v_ratio / 100
    if h < 0:
      left = -2 * (h * h) + 1
      if left >= 0:
        right = 2 - left
      else:
        right = 2
    else:
      right = -2 * (h * h) + 1
      if right >= 0:
        left = 2 - right
      else:
        left = 2
    left *= v
    right *= v
    left = -max(min(left * 100, 100), -100)
    right = -max(min(right * 100, 100), -100)
    self.logger.debug("Sending motor update l/r: " + left + "/" + right)
    self.client.publish("robo/motor/left/speed", left, 0, True)
    self.client.publish("robo/motor/right/speed", right, 0, True)

  def reset(self):
    self.client.publish("robo/joystick/h/ratio", 0, 0, True)
    self.client.publish("robo/joystick/v/ratio", 0, 0, True)

  def start(self):
    self.client.loop_start()
    self.reset()

  def stop(self):
    self.client.loop_stop(True)
