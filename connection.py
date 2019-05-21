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


class FakeConnection:
    """Fake connection that can be used for testing the GUI."""
    def __init__(self, *args, **kwargs):
        from gain_camera.parameters import Parameters
        self.parameters = Parameters()
        self.image_data = [np.array([[1,2], [3,4]])] * 3

    def connect(self):
        pass

    def run_continuous_acquisition(self):
        pass

    def record_background(self):
        self.parameters.background.value = [self.image_data] * 9

    def clear_background(self):
        self.parameters.background.value = None


class Connection(BaseClient):
    def run_continuous_acquisition(self):
        self.parameters.continuous_acquisition.value = True

        def do_change(data):
            self.image_data = msgpack.unpackb(data)
        self.parameters.live_imgs.change(do_change)

    def stop_continuous_acquisition(self):
        self.parameters.continuous_acquisition.value = False

    def enable_trigger(self, enable):
        self.parameters.trigger.value = enable

    def set_exposure_time(self, exposure):
        assert exposure in EXPOSURES
        self.parameters.exposure.value = exposure

    def snap_image(self, cam_idx, subtract=False):
        return self.connection.root.exposed_snap_image(cam_idx, subtract=subtract)

    def retrieve_image(self, cam_idx, subtract=False):
        return self.connection.root.exposed_retrieve_image(cam_idx, subtract=subtract)

    def wait_till_frame_ready(self, cam_idx):
        """Waits until camera `cam_idx` receives a trigger."""
        return self.connection.root.exposed_wait_till_frame_ready(cam_idx)

    def reset_frame_ready(self, cam_idx):
        return self.connection.root.exposed_reset_frame_ready(cam_idx)

    def record_background(self):
        """Records a background image for all exposures that will be subtracted
        automatically for future images."""
        self.parameters.trigger.value = False
        # stop continuous acquisition
        self.parameters.continuous_acquisition.value = False
        # wait some time to be sure that acquisition is really stopped
        # we have to do this because it may be waiting for a trigger
        sleep(.75)
        self.connection.root.exposed_record_background()
        # start continuous acquisition again
        self.parameters.continuous_acquisition.value = True

    def clear_background(self):
        """Clears the background image."""
        self.parameters.background.value = None