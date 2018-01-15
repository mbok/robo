# Import the PCA9685 module.
import Adafruit_PCA9685


class PwmControl:
  # Configure min and max servo pulse lengths
  servo_min = 150  # Min pulse length out of 4096
  servo_max = 600  # Max pulse length out of 4096

  def __init__(self):
    self.pwm = Adafruit_PCA9685.PCA9685()
    # Set frequency to 60hz, good for servos.
    self.pwm.set_pwm_freq(60)

  def pulseRatio(self, channel, ratio):
    self.pwm.set_pwm(channel, 0, int(round(ratio / 100.0 * 4095)))
