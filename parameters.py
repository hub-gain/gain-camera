import numpy as np

from gain_camera.utils import EXPOSURES
from gain_camera.communication.server import Parameter, BaseParameters


class Parameters(BaseParameters):
    def __init__(self):
        super().__init__()

        self.exposure = Parameter(start=-2, min_=np.min(EXPOSURES), max_=np.max(EXPOSURES))
        self.background = Parameter()
        self.crop_enabled = Parameter(start=True)
        self.crop = Parameter(start=(0, 744, 0, 480))
        self.live_imgs = Parameter()
        self.trigger = Parameter(start=False)
        self.continuous_acquisition = Parameter(start=False)

        # the following parameters are used by the live view client
        self.recording = Parameter(start=True)
        self.recording_length = Parameter(start=400)
        self.clear_recording = Parameter(start=False)