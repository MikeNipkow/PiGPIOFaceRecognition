# PiGPIOFaceRecognition
Toggle Raspberry Pi GPIOs when a camera detects an authorized person.

Using ``face_recognition`` this script can toggle the GPIOs of a Raspberry Pi with ``pigpio``.

# Features
You can connect a camera via an __rtsp stream__ or using a directly connected camera. The script will scan the current frame for faces and compare those to your defined reference images. If any face matches a reference face a GPIO of your pi will be turned on for a defined amount of time.

``PiGPIOFaceRecognition`` will automatically draw a box around the recognized faces and save the frame if an authorized person was found and the GPIO therefore turned on. If your reference image contain the persons name, e.g. ``Alex.png`` it will also display their names in the console and their name will be put under the drawn box in the frame.
