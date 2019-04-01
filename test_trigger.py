from matplotlib import pyplot as plt
import numpy as np
from gain_connection import Connection

c = Connection()
c.connect()
#c.enable_trigger(False)
#plt.pcolormesh(c.snap_image(0))
#plt.show()
#c.enable_trigger(True)

#c.connection.root.cams[0].cam.wait_til_frame_ready()

#cam = c.connection.root.cams[0].cam
"""try:
    cam.suspend_live()
except:
    print('not live')

input('ready for calibration?')

for i in range(4):
    try:
        cam.start_live()
    except:
        print('start live failed')
    cam.snap_image()
    cam.get_image_data()
    cam.suspend_live()

cam.enable_continuous_mode(True)
cam.start_live()
if not cam.callback_registered:
    cam.register_frame_ready_callback()

cam.enable_trigger(True)

input('ready?')

#cam.reset_frame_ready()

from time import sleep
sleep(1)"""

cam_idx = 1

try:
    c.enable_trigger(True, [cam_idx])
except:
    print('enabling failed!')

for i in range(2):
    c.reset_frame_ready(cam_idx)
    #cam.reset_frame_ready()
    #cam.wait_til_frame_ready()
    c.wait_till_frame_ready(cam_idx)
    print('ready!')
    plt.pcolormesh(c.retrieve_image(cam_idx))
    plt.show()

    #data = cam.get_image_data()
    #print('DATA!')
    #print(data)
    #plt.pcolormesh(cam.get_image_data())
    #plt.show()