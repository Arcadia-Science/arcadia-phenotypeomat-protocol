import sys as sys
import time as tm

import cam_tools as ct
import serial as ser

"""This is a script that highlights most of the functions available in cam_tools.py.
It connects to the microcontroller, sets up the camera, turns on the grow lights,
allows the use of a barcode reader, turns on the LEDs that are useful for Chlamydomonas
to grow ("grow lights"), then acquires an image using transillumination once an hour
for 48 hours"""

dev = ser.Serial("/dev/ttyACM0")  # establish serial communication with microcontroller

dev.write(b"SET LED_TRANS_STATUS 1;")  # turn off the LED

if not ct.detect_cams():  # make sure there are blackfly cameras attached to the computer
    sys.exit()

system = ct.ps.System.GetInstance()  # start the communication to the cameras

cam_list = system.GetCameras()  # get the handles of the cameras

cam = cam_list[0]  # set a handle for a specific camera

cam.Init()  # initialze the camera

dev.write(b"SET LED_TRANS_STATUS 0;")  # turn on the led
dev.write(b"SET LED_460_STATUS 0;")  # turn on grow light
dev.write(b"SET LED_670_STATUS 0;")  # turn on grow light

bcode = ct.bcode_read()  # get barcode from usb barcode reader

input("hit enter to start assay")  # start the assay

for _n in range(0, 48):
    ct.set_expos_time(cam, 500)  # set the exposure time
    dev.write(b"SET LED_460_STATUS 1;")  # turn off grow light
    dev.write(b"SET LED_670_STATUS 1;")  # turn off grow light
    dev.write(b"SET LED_TRANS_STATUS 0;")  # turn on the led
    tm.sleep(5)  # wait 5 seconds
    images, timestamps = ct.grab_images(
        cam, n_frames=1
    )  # get images and timestamps for a vide of 10 seconds length from the camera
    ct.save_avi(images, barcode=bcode, prefix="algae_growth_curve")  # save images
    dev.write(b"SET LED_460_STATUS 0;")  # turn on grow light
    dev.write(b"SET LED_670_STATUS 0;")  # turn on grow light
    tm.sleep(60 * 60)  # wait 1 hr
    dev.write(b"SET LED_TRANS_STATUS 1;")  # turn off LED

print(str(timestamps[-1] - timestamps[0]))  # print the total imaging time
print(str(timestamps[-1] - timestamps[-2]))  # print the time between frames

dev.write(b"SET LED_TRANS_STATUS 1;")  # turn off the led

del cam  # turn off the camera

cam_list.Clear()  # de-initialize the cameras

system.ReleaseInstance()  # release the handlers
