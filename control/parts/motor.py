import RPi.GPIO as GPIO


class Motor:
  def __init__(self, pin_in1, pin_in2, pwm, pwm_channel):
    self.pin_in1 = pin_in1
    self.pin_in2 = pin_in2
    self.pwm_channel = pwm_channel
    self.pwm = pwm
    GPIO.setup(self.pin_in1, GPIO.OUT)
    GPIO.setup(self.pin_in2, GPIO.OUT)

  def backward(self, ratio):
    GPIO.output(self.pin_in1, GPIO.HIGH)
    GPIO.output(self.pin_in2, GPIO.LOW)
    self.pwm.pulseRatio(self.pwm_channel, ratio)

  def forward(self, ratio):
    GPIO.output(self.pin_in1, GPIO.LOW)
    GPIO.output(self.pin_in2, GPIO.HIGH)
    self.pwm.pulseRatio(self.pwm_channel, ratio)

  def speed(self, ratio):
    if (ratio < 0.0):
      self.backward(-1 * ratio)
    elif (ratio > 0.0):
      self.forward(ratio)
    else:
      self.stop()

  def stop(self):
    GPIO.output(self.pin_in1, GPIO.LOW)
    GPIO.output(self.pin_in2, GPIO.LOW)
    self.pwm.pulseRatio(self.pwm_channel, 0)