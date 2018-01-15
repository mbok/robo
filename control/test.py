import time
import logging
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
  print("Connected with result code " + str(rc))
  # client.subscribe("robo/#")

client = mqtt.Client()
client.on_connect = on_connect

client.connect("localhost", 1883, 60)

client.loop_start()

i = 90
while i <= 100:
  print ("Set speed " + str(i))
  client.publish("robo/motor/left/speed", str(i / 100.0))
  client.publish("robo/motor/right/speed", str(i / -100.0))
  time.sleep(1)
  i += 1

client.publish("robo/motor/left/speed", str(0))
client.publish("robo/motor/right/speed", str(0))


client.loop_stop()