Software for accessing the GAIN fluorescence cameras. As the USB connection requires exclusive access, a server-client architecture was used that allows for (multiple) live view applications to be running while at the same time enabling programmatical access.

# Usage
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
## Programmatical access
```
from time import sleep
from matplotlib import pyplot as plt
from gain_camera.connection import CameraConnection

c = CameraConnection('gain.physik.hu-berlin.de',  8000)
c.set_exposure_time(-10)
c.enable_trigger(True)
c.reset_frame_ready(0)
c.wait_till_frame_ready(0)
print('trigger received!')

for idx in range(3):
    plt.pcolormesh(c.snap_image(idx))
    plt.show()

c.enable_trigger(False)
# start "continuous acquisition" mode. This means that the server records 
# images autonomously as fast as possible. The result is saved in the
# `live_imgs` parameter.
c.start_continuous_acquisition()
sleep(1)
plt.pcolormesh(c.parameters.live_imgs.value[0])
plt.show()

# we can also react when an image has been recorded
def new_img_recorded(imgs):
    print('new image!')
c.parameters.live_imgs.change(new_img_recorded)

while True:
    c.parameters.call_listeners(auto_queue=False)

    # do something else
    sleep(5)
```

