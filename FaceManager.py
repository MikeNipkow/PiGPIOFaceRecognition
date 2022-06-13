import datetime
import os, face_recognition

# This class handles the authorized persons.
import time
from threading import Thread

import cv2

from AuthorizedPerson import AuthorizedPerson
from ConfigManager import ConfigManager
from api import Util


class FaceManager:
    # Instance of ConfigManager.
    config = None

    # List of all authorized persons and their faces.
    authorized_persons = []
    temp_authorized_persons = []
    encoded_faces = []
    temp_encoded_faces = []

    # Constructor.
    def __init__(self, config):
        assert isinstance(config, ConfigManager)

        # Store vars.
        self.config = config

        # Load authorized persons on startup.
        self.load_authorized_persons()

        # Create a separate thread to reload the config.
        # self.thread = Thread(target=self.__reload_authorized_persons)
        # self.thread.daemon = True
        # self.thread.start() # May cause huge performance issues.

    # Reload authorized persons.
    def __reload_authorized_persons(self):
        while True:
            time.sleep(self.config.config_settings_config_reload_interval)
            self.load_authorized_persons()

    # Load authorized persons.
    def load_authorized_persons(self):
        # Get path where the authorized images are stored.
        image_path = self.config.config_facerecognition_reference_path

        # Create folder if it does not already exist.
        try:
            os.mkdir(image_path)
        except FileExistsError:
            pass

        # Loop through every file in the folder.
        for file_name in os.listdir(image_path):
            # Load image.
            image = cv2.imread(image_path + "/" + file_name)

            # Check if file is an image.
            if image is None:
                continue

            # Get name of the person by filename.
            split_file_name = file_name.split("_")
            name = split_file_name[0] if len(split_file_name) > 1 \
                else file_name.replace(".png", "").replace(".jpg", "")

            # Get faces out of the image.
            face_locations = face_recognition.face_locations(image)
            encoded_faces = face_recognition.face_encodings(image, face_locations)

            # Handle amount of faces in the image.
            if len(encoded_faces) <= 0:
                if self.config.config_settings_debug:
                    Util.log("No face found in image " + file_name + " -  Skipping...")
                continue

            elif len(encoded_faces) > 1:
                if self.config.config_settings_debug:
                    Util.log("More than one face found in " + file_name + " - Skipping...")
                continue

            else:
                # Add person to the whitelist.
                authorized_person = AuthorizedPerson(name, file_name, image, encoded_faces[0])
                self.temp_authorized_persons.append(authorized_person)
                self.temp_encoded_faces.append(encoded_faces[0])

        # Move temp vars to live vars.
        self.authorized_persons = self.temp_authorized_persons.copy()
        self.encoded_faces = self.temp_encoded_faces.copy()

        # Clear temporary vars.
        self.temp_authorized_persons.clear()
        self.temp_encoded_faces.clear()

        # Print authorized persons.
        if self.config.config_settings_debug:
            # Check how many persons are authorized.
            amount = len(self.authorized_persons)
            Util.log("Found " + str(amount) + " authorized persons" + (":" if amount > 0 else "."))

            # Loop through every person to print information about them.
            for authorized_person in self.authorized_persons:
                Util.log(" - " + authorized_person.name + ": " + authorized_person.image_path)

    # Get all authorized persons and their encoded faces.
    def get_authorized_persons_and_faces(self):
        return self.authorized_persons, self.encoded_faces

    # Frame face in image
    def frame_face(self, frame, verified, name, left, top, right, bottom):
        color = (0, 255, 0) if verified else (0, 0, 255)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        self.print_capture_info(name)

    # Info if person was detected
    def print_capture_info(self, name):
        Util.log("Person found: " + name)

    # Save frame.
    def save_frame(self, img):
        # Dir path.
        dir_path = self.config.config_facerecognition_save_path

        # Create dir.
        try:
            os.mkdir(dir_path)
        except FileExistsError:
            pass

        current_datetime = datetime.datetime.now()
        date = "%s.%s.%s" % (current_datetime.day, current_datetime.month, current_datetime.year)
        time = "%s.%s.%s" % (current_datetime.hour, current_datetime.minute, current_datetime.second)
        filename = Util.convert_string_to_path(dir_path + "/" + date + "_" + time + ".png")
        result = cv2.imwrite(filename, img)

        # Log message.
        if self.config.config_settings_debug:
            Util.log("Successfully saved image of authorized person." if result else
                     "Could not save the image of the authorized person.")

    # Get all face locations and encodings in a frame.
    @staticmethod
    def get_face_locations_and_encodings(frame):
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        return face_locations, face_encodings
