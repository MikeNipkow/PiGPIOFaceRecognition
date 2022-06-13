import os.path

import cv2
import face_recognition

from ConfigManager import ConfigManager
from FaceManager import FaceManager
from RaspberryPiManager import RaspberryPiManager
from VideoManager import VideoManager
from api import Util

# Check if file was run as script.
if __name__ != "__main__":
    Util.log("This python file needs to be run as a script.")
    exit()

# Get project root.
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# Create instance of ConfigManager.
config = ConfigManager(ROOT_DIR)

# Create instance of RaspberryPi Manager.
pi_manager = RaspberryPiManager(config)

# Create instance of FaceManager.
face_manager = FaceManager(config)

# Create instance of VideoManager.
video_manager = VideoManager(config)

# Schleife
while True:
    # Get current frame.
    frame_bgr = video_manager.read()

    # Null check.
    if frame_bgr is None:
        continue

    # Convert BGR to RGB.
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

    # Null check
    if frame_rgb is None:
        continue
    # Get all faces in current frame.
    face_locations, face_encodings = FaceManager.get_face_locations_and_encodings(frame_rgb)

    # Var to check if door will be opened by this frame.
    door_opened_before = pi_manager.is_on()

    # Check if any face is authorized.
    any_authorized_face = False

    # Loop through all the faces found in the current frame.
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Var to check if the person is authorized or not
        authorized = False

        # Compare face with the authorized faces.
        matches = face_recognition.compare_faces(face_manager.encoded_faces, face_encoding,
                                                 tolerance=config.config_facerecognition_tolerance)

        # Check if a face matches.
        for i in range(len(matches)):
            # Continue, if it doesn't match 100%.
            if not matches[i]:
                continue

            # Get name.
            name = face_manager.authorized_persons[i].name

            # Draw a frame around the face.
            face_manager.frame_face(frame_bgr, True, name, left, top, right, bottom)

            # End loop
            authorized = True
            any_authorized_face = True

        # Also frame face, if the person is unknown.
        if not authorized:
            face_manager.frame_face(frame_bgr, False, config.config_settings_unknown_name, left, top, right, bottom)

    # Open or close door
    if any_authorized_face:
        pi_manager.toggle_on()
    else:
        pi_manager.toggle_off()

    # Save the image, if the door will be opened by this image.
    if not door_opened_before and pi_manager.is_on():
        face_manager.save_frame(frame_bgr)

video_manager.release()
pi_manager.force_toggle_off()