import RPi.GPIO as GPIO


class Motor:
  def __init__(self, pin_in1, pin_in2, pwm, pwm_channel):
    self.pin_in1 = pin_in1
    self.pin_in2 = pin_in2
    self.pwm_channel = pwm_channel
    GPIO.setup(self.pin_in1, GPIO.OUT)
    GPIO.setup(self.pin_in2, GPIO.OUT)


def backward(self):
  GPIO.output(self.pin_in1, GPIO.HIGH)
  GPIO.output(self.pin_in2, GPIO.LOW)


def backward(self):
  GPIO.output(self.pin_in1, GPIO.HIGH)
  GPIO.output(self.pin_in2, GPIO.LOW)


def speed(self, ratio):
  pwm.pulseRatio(self.pwm_channel, ratio)
