"""
Contains a definition of the parameters that are used. The parameters' valuee are
accessible by client and server, and both parties can register listeners that are called
when a value changes.
"""
import numpy as np

from .communication.server import BaseParameters, Parameter
from .utils import EXPOSURES


class Parameters(BaseParameters):
    def __init__(self):
        super().__init__()

        # the exposure time of the cameras (-2 to -13)
        # exposure time in ms: 250 / (2**exposure)
        self.exposure = Parameter(
            start=-2, min_=np.min(EXPOSURES), max_=np.max(EXPOSURES)
        )
        self.background = Parameter()
        self.crop_enabled = Parameter(start=True)
        self.crop = Parameter(start=(0, 744, 0, 480))

        # are the cameras in continuous acquisition mode?
        self.continuous_acquisition = Parameter(start=False)

        # if the server is in "continuous acquisition" mode, the recorded images will be
        # stored here
        self.live_imgs = Parameter(collapsed_sync=True)
        self.live_atom_number = Parameter()

        # should the cameras wait for an external trigger?
        self.trigger = Parameter(start=False)

        # the following parameters are used by the live view client
        # should the atom numbers be recorded?
        self.recording = Parameter(start=True)
        # how many samples to record?
        self.recording_length = Parameter(start=400)
        self.clear_recording = Parameter(start=False)
