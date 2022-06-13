import configparser
import os
import shutil
# This class is used to manage the configuration.
import time
from threading import Thread

from api import Util


class ConfigManager:
    # Path to files.
    root_dir = None
    config_path = None
    default_config_path = None

    # Config
    config = None

    # Sections in the configuration.
    section_camera = "CAMERA"
    section_raspberrypi = "RASPBERRY PI"
    section_facerecognition = "FACE RECOGNITION"
    section_settings = "SETTINGS"

    # Config options.
    config_camera_camera_data = "rtsp://USER:PASSWORD:554/stream1"
    config_camera_connection_check_interval = 60.0

    config_raspberrypi_ip_address = "192.168.1.1"
    config_raspberrypi_gpio = 21
    config_raspberrypi_invert_output = False
    config_raspberrypi_min_output_duration = 3.0
    config_raspberrypi_connection_check_interval = 60.0

    config_facerecognition_tolerance = 0.12
    config_facerecognition_reference_path = "<ROOT>/images"
    config_facerecognition_save_authorized_images = True
    config_facerecognition_save_path = "<ROOT>/history"

    config_settings_unknown_name = "Unknown"
    config_settings_config_reload_interval = 60.0
    config_settings_debug = False

    # Constructor
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.config_path = root_dir + "/config.ini"
        self.default_config_path = root_dir + "/default/config.ini"

        # Load config at startup.
        self.config = configparser.ConfigParser()
        self.setup_config()

        # Create a separate thread to reload the config.
        self.thread = Thread(target=self.__reload_config)
        self.thread.daemon = True
        self.thread.start()

    # Check if a configuration file exists.
    def config_exists(self):
        return os.path.exists(self.config_path)

    # Copy default config to project root.
    def copy_default_config(self):
        # Check if default config exists.
        try:
            shutil.copyfile(self.default_config_path, self.config_path)
            return True
        except Exception as ex:
            print(ex)
            Util.log("Could not copy the default file to project root.")
            return False

    # Reload config every x seconds.
    def __reload_config(self):
        while True:
            time.sleep(self.config_settings_config_reload_interval)
            self.setup_config()

    # Load the configuration.
    def setup_config(self):
        # Copy default config to project root if it does not exist.
        if not self.config_exists() and not self.copy_default_config():
            raise FileNotFoundError("The default config could not be copied to the project root.")

        # Load configuration.
        self.config.read(self.config_path)

        # Debug info.
        if self.config_settings_debug:
            Util.log("Reloading config...")

        # Load configuration sections.
        configsection_camera = self.config[self.section_camera]
        configsection_raspberrypi = self.config[self.section_raspberrypi]
        configsection_facerecognition = self.config[self.section_facerecognition]
        configsection_settings = self.config[self.section_settings]

        # Load values.
        # Camera section.
        self.config_camera_camera_data = \
            configsection_camera.get("CameraData", self.config_camera_camera_data)
        self.config_camera_connection_check_interval = \
            configsection_camera.get("ConnectionCheckInterval", self.config_camera_connection_check_interval)

        # RaspberryPi section.
        self.config_raspberrypi_ip_address = \
            configsection_raspberrypi.get("IP-Address", self.config_raspberrypi_ip_address)
        self.config_raspberrypi_gpio = \
            configsection_raspberrypi.getint("GPIO", self.config_raspberrypi_gpio)
        self.config_raspberrypi_invert_output = \
            configsection_raspberrypi.getboolean("InvertOutput", self.config_raspberrypi_invert_output)
        self.config_raspberrypi_min_output_duration = \
            configsection_raspberrypi.getfloat("MinOutputDuration", self.config_raspberrypi_min_output_duration)
        self.config_raspberrypi_connection_check_interval = \
            configsection_raspberrypi.getfloat("ConnectionCheckInterval",
                                               self.config_raspberrypi_connection_check_interval)

        # Face recognition section.
        self.config_facerecognition_tolerance = \
            configsection_facerecognition.getfloat("Tolerance", self.config_facerecognition_tolerance)
        self.config_facerecognition_reference_path = \
            configsection_facerecognition.get("ReferencePath", self.config_facerecognition_reference_path) \
                                         .replace("<ROOT>", self.root_dir)
        self.config_facerecognition_save_authorized_images = \
            configsection_facerecognition.getboolean("SaveAuthorizedImages",
                                                     self.config_facerecognition_save_authorized_images)
        self.config_facerecognition_save_path = \
            configsection_facerecognition.get("SavePath", self.config_facerecognition_save_path) \
                                         .replace("<ROOT>", self.root_dir)

        # Settings section.
        self.config_settings_unknown_name = configsection_settings.get("UnknownName", self.config_settings_unknown_name)
        self.config_settings_config_reload_interval = \
            configsection_settings.getfloat("ConfigReloadInterval", self.config_settings_config_reload_interval)
        self.config_settings_debug = configsection_settings.getboolean("Debug", self.config_settings_debug)
