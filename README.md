Software for accessing the GAIN fluorescence cameras. As the USB connection requires exclusive access, a server-client architecture was used that allows for (multiple) live view applications to be running while at the same time enabling programmatical access.

# Usage
As git submodule is used, you should check out the code like this:

..  code-block:: bash

    git clone https://git.physik.hu-berlin.de/gain/gain_camera.git --recursive

## Server
* Runs on windows only as it relies on a DLL that is not available for linux
* Can be started like this:
```
python3 -m gain_camera.camera_server
```
## Live view GUI
* Runs on linux and windows (untested)
* Multiple instances can be launched
```
python3 -m gain_camera.live_view
```
## Scripting
```
import msgpack
import msgpack_numpy as m
m.patch()

from time import sleep
from matplotlib import pyplot as plt
from gain_camera.connection import CameraConnection

c = CameraConnection('gain.physik.hu-berlin.de', 8000)

# retrieve parameters
# see https://git.physik.hu-berlin.de/gain/gain_camera/blob/master/parameters.py
# for a list of parameters and their meaning.
print('Exposure', c.parameters.exposure.value)

# record images
# this doesn't work properly if the live view application was started previously.
# in that case, turn off and on the cameras and restart the camera server.
c.set_exposure_time(-10)
c.enable_trigger(True)
c.reset_frame_ready(0)
c.wait_till_frame_ready(0)
print('trigger received!')

for idx in range(3):
    plt.pcolormesh(c.snap_image(idx))
    plt.show()

c.enable_trigger(False)

# start "continuous acquisition" mode. This is what happens when you start the
# camera live view application. It means that the server records images
# autonomously as fast as possible. The result is saved in the `live_imgs` parameter.
c.run_continuous_acquisition()
sleep(1)
images = msgpack.unpackb(c.parameters.live_imgs.value)
plt.pcolormesh(images[0])
plt.show()

# we can also react when an image has been recorded
def new_img_recorded(imgs):
    print('new image!')
c.parameters.live_imgs.change(new_img_recorded)

while True:
    # this checks periodically whether a new image arrived and calls the
    # listener (`new_img_recorded()`)
    c.parameters.call_listeners()

    # here you can do something else
    sleep(.1)

# we can also capture a time record of atom numbers
c.run_continuous_acquisition()
sleep(1)
c.set_exposure_time(-2)
c.parameters.recording.value = True
c.parameters.recording_length = 500

def atom_number_received(value):
    print('recorded atom number:', value)

c.parameters.live_atom_number.change(atom_number_received)
```