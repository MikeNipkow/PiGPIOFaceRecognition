from threading import Thread

import cv2

# This class is used to always get the latest image of a cv2.Videocapture() stream.
from ConfigManager import ConfigManager
from api import Util


class VideoManager:

    # Var to check if the information about the disconnect was sent.
    disconnect_message_shown = False

    # Link to the stream.
    video_link = None

    # Constructor.
    def __init__(self, config):
        assert isinstance(config, ConfigManager)

        # Store vars.
        self.config = config

        # Get stream link.
        self.video_link = config.config_camera_camera_data

        # Connect to video device.
        self.connect()

        # Create a separate thread to check the connection.
        self.thread = Thread(target=self.__reader)
        self.thread.daemon = True
        self.thread.start()

    # Check connection to the stream.
    def connected(self):
        return self.cap is not None and self.cap.isOpened()

    # Grab frames as soon as they are available.
    def __reader(self):
        while True:
            # Check if the stream link has changed.
            if self.video_link != self.config.config_camera_camera_data:
                Util.log("Address of the Video-Stream has changed: " +
                         self.video_link + " → " + self.config.config_camera_camera_data)
                self.video_link = self.config.config_camera_camera_data

                # Close current stream.
                if not self.connected():
                    self.release()

            # Reopen connection to the stream, if not available yet.
            if not self.connected():
                if not self.disconnect_message_shown:
                    Util.log("No video device connected with stream link: " + self.video_link)
                    Util.log("Attempting to reconnect...")

                # Try to reconnect.
                self.connect()

            ret = self.cap.grab()

    # Connect to video device.
    def connect(self):
        try:
            self.cap = cv2.VideoCapture(int(self.video_link))
        except ValueError:
            self.cap = cv2.VideoCapture(self.video_link)

        # Check if stream is reconnected.
        if self.connected():
            Util.log("Successfully connected to the video stream.")
            self.disconnect_message_shown = False
        elif not self.disconnect_message_shown:
            Util.log("Failed to connect to the video stream.")
            self.disconnect_message_shown = True

    # Get latest frame.
    def read(self):
        ret, frame = self.cap.retrieve()
        return frame

    # Release stream.
    def release(self):
        self.cap.release()
