"""
    gain_camera.connection
    ~~~~~~~~~~~~~~~~~~~~~~

    Contains the client that can be used to access a camera server.
"""
import numpy as np
from time import sleep
from gain_camera.utils import EXPOSURES
from gain_camera.communication.client import BaseClient

import msgpack
import msgpack_numpy as m
m.patch()


class CameraConnection(BaseClient):
    """Connection to the camera server.

    This class can be used to control the cameras programatically. Use the live
    view client to display a GUI.

    Usage:

        c = CameraConnection(host, port)

    This class contains several methods that are proxies to the server
    counterparts. Furthermore, several parameters can be controlled like this:

        c.parameters.exposure = -10
        c.run_continuous_acquisition()
        sleep(1)
        plt.pcolormesh(c.parameters.live_imgs.value[0])
        plt.show()
    """
    def __init__(self, server, port, keep_in_sync=False):
        super().__init__(server, port, keep_in_sync)

    def run_continuous_acquisition(self):
        """Runs continuous acquisition.

        This means that the server will record images as fast as possible and
        store them in `parameters.live_imgs`."""
        self.image_data = None
        self.atom_number_data = []
        self.parameters.continuous_acquisition.value = True

        def do_change(data):
            if data is not None:
                print('received data')
                self.image_data = msgpack.unpackb(data)
        self.parameters.live_imgs.change(do_change)
        def atom_number_changed(atom_number):
            if atom_number is not None:
                self.atom_number_data.append(atom_number)
        self.parameters.live_atom_number.change(atom_number_changed)

    def stop_continuous_acquisition(self):
        self.parameters.continuous_acquisition.value = False

    def enable_trigger(self, enable):
        """Should the cameras wait for trigger?"""
        self.parameters.trigger.value = enable

    def set_exposure_time(self, exposure):
        assert exposure in EXPOSURES, \
            ('invalid exposure times. Valid values are %s' % str(EXPOSURES))
        self.parameters.exposure.value = exposure

    def snap_image(self, cam_idx, subtract=False):
        """Records and retrieves an image.

        Use `subtract` to enable background subtraction."""
        return self.connection.root.snap_image(cam_idx, subtract=subtract)

    def retrieve_image(self, cam_idx, subtract=False):
        """Retrieves an image (that was previously recorded).

        Use `subtract` to enable background subtraction."""
        return self.connection.root.retrieve_image(cam_idx, subtract=subtract)

    def wait_till_frame_ready(self, cam_idx):
        """Waits until camera `cam_idx` receives a trigger."""
        return self.connection.root.wait_till_frame_ready(cam_idx)

    def reset_frame_ready(self, cam_idx):
        return self.connection.root.reset_frame_ready(cam_idx)

    def record_background(self):
        """Records a background image for all exposures that will be subtracted
        automatically for future images."""
        self.parameters.trigger.value = False
        # stop continuous acquisition
        self.parameters.continuous_acquisition.value = False
        # wait some time to be sure that acquisition is really stopped
        # we have to do this because it may be waiting for a trigger
        sleep(.75)
        self.connection.root.record_background()
        # start continuous acquisition again
        self.parameters.continuous_acquisition.value = True

    def clear_background(self):
        """Clears the background image."""
        self.parameters.background.value = None