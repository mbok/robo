# Import the PCA9685 module.
import Adafruit_PCA9685

pwm = Adafruit_PCA9685.PCA9685()
# Set frequency to 60hz, good for servos.
pwm.set_pwm_freq(60)

class PwmMotorControl:
  def __init__(self, channel):
    self.channel = channel

  def ratio(self, ratio):
    pwm.set_pwm(self.channel, 0, int(round(ratio / 100.0 * 4095)))


class PwmServoControl:
  # Configure min and max servo pulse lengths
  servo_min = 150  # Min pulse length out of 4096
  servo_max = 600  # Max pulse length out of 4096

  def __init__(self, channel):
    self.channel = channel
    self.trim = 0.0
    self.ratio = 0.0

  def ratio(self, ratio):
    if (ratio >= -100 and ratio <= 100):
      self.ratio = ratio
    self.apply()

  def trim(self, trim):
    if (trim > -100 and trim < 100):
      self.trim = trim
    self.apply()

  def apply(self):
    mid = self.servo_min + (self.servo_max - self.servo_min) / 2.0 * (1 + self.trim / 100.0)
    pulse_start = mid
    if (self.ratio > 0):
      pulse_start += (self.servo_max - mid) * self.ratio / 100.0
    elif (self.ratio < 0):
      pulse_start += (mid - self.servo_min) * self.ratio / 100.0
    pwm.set_pwm(self.channel, 0, int(pulse_start))

