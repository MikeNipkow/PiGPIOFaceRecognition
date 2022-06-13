import atexit
import time
from threading import Thread

import pigpio as pigpio

from ConfigManager import ConfigManager
from api import Util
# This class is used to handle the RaspberryPis IO's via GPIO.
from api.Timer import Timer


class RaspberryPiManager:
    # Config
    config = None

    # Instance of RaspberryPi.
    pi = None

    # IP-Address of the RaspberryPi
    current_address = None

    # Var to check if door is open.
    toggle = False

    # Var to check if the door was open the last time it was checked.
    last_gpio_state = False

    # Constructor.
    def __init__(self, config):
        assert isinstance(config, ConfigManager)

        # Store vars.
        self.config = config
        self.address = self.config.config_raspberrypi_ip_address
        self.timer = Timer(self.config.config_raspberrypi_min_output_duration)

        # Establish connection on startup.
        self.connect()

        # Create handler to close door on program exit.
        atexit.register(self.force_toggle_off)

        # Create a separate thread to check the connection.
        self.thread = Thread(target=self.__check_connection)
        self.thread.daemon = True
        self.thread.start()

    # Check connection.
    def __check_connection(self):
        while True:
            time.sleep(self.config.config_raspberrypi_connection_check_interval)
            self.connect()

    # Setup connection.
    def connect(self):
        # Check if configured ip address has changed - if not just return.
        if self.address != self.get_configured_ip_address():
            Util.log("IP-Address of RaspberryPi has changed: " +
                     self.address + " → " + self.config.config_raspberrypi_ip_address)
            self.address = self.get_configured_ip_address()
        elif self.connected():
            return

        # Connect to pi.
        Util.log("Trying to establish the connection to RaspberryPi on: " + self.address)
        self.pi = pigpio.pi(self.address)

        # Log if the connection was successful or not.
        if self.pi.connected:
            Util.log("Successfully connected to RaspberryPi.")
        else:
            Util.log("Failed to connect to RaspberryPi.")

    # Check if RaspberryPi is connected.
    def connected(self):
        return False if self.pi is None else self.pi.connected

    # Get configured ip address from config file.
    def get_configured_ip_address(self):
        return self.config.config_raspberrypi_ip_address

    # Get configured gpio from config file.
    def get_gpio(self):
        return self.config.config_raspberrypi_gpio

    # Open GPIO.
    def toggle_on(self):
        self.toggle = True
        self.__handle_gpio()

    # Close GPIO.
    def toggle_off(self):
        self.toggle = False
        self.__handle_gpio()

    # Force GPIO to turn off.
    def force_toggle_off(self):
        Util.log("Forcing GPIO to turn off...")
        invert = self.config.config_raspberrypi_invert_output
        self.pi.write(self.config.config_raspberrypi_gpio, False if not invert else True)

    # Check if GPIO is on.
    def is_on(self):
        return not self.timer.expired()

    # Handle GPIO state..
    def __handle_gpio(self):
        if not self.pi.connected:
            return

        invert = self.config.config_raspberrypi_invert_output
        if self.toggle:
            if not self.is_on():
                Util.log("Opening door...")

            self.timer.start()
            self.pi.write(self.config.config_raspberrypi_gpio, True if not invert else False)
        elif self.timer.expired():
            self.pi.write(self.config.config_raspberrypi_gpio, False if not invert else True)
            self.timer = Timer(self.config.config_raspberrypi_min_output_duration)

            if self.last_gpio_state:
                Util.log("Closing door...")

        self.last_gpio_state = self.is_on()
