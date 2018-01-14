import time
import logging
import paho.mqtt.client as mqtt
import parts.motor as parts

logging.basicConfig(level=logging.DEBUG)


def on_connect(client, userdata, flags, rc):
  print("Connected with result code " + str(rc))

# client = mqtt.Client()
# client.on_connect = on_connect

# client.connect("localhost", 1883, 60)

# client.loop_start()

motorLeft = parts.Motor(26, 20, 15)

# while True:
#  time.sleep(2)
#  client.publish("test/temperature", "test")