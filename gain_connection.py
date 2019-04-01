import rpyc
import dill
import pickle
import uuid
import numpy as np
from time import sleep
from threading import Thread
from gain_camera.parameters import Parameters

from pyqtgraph.Qt import QtCore

import msgpack
import msgpack_numpy as m
m.patch()


class FakeConnection:
    """Fake connection that can be used for testing the GUI."""
    def __init__(self, *args, **kwargs):
        self.parameters = Parameters()
        self.image_data = [np.array([[1,2], [3,4]])] * 3

    def connect(self):
        pass

    def run_acquisition_thread(self):
        pass

    def record_background(self):
        self.parameters.background.value = [self.image_data] * 9

    def clear_background(self):
        self.parameters.background.value = None


class Connection:
    def connect(self):
        self.image_data = [None] * 3
        self.connection = rpyc.connect('gain.physik.hu-berlin.de', 8000)
        self.uuid = uuid.uuid4().hex
        self.parameters = RemoteParameters(
            self.connection.root.parameters,
            self.uuid
        )

    def run_acquisition_thread(self):
        self.parameters.continuous_acquisition.value = True

        def retrieve_data():
            def do_change(data):
                self.image_data = msgpack.unpackb(data)
            self.parameters.live_imgs.change(do_change)

        self.thread = Thread(target = retrieve_data, args = tuple(), daemon=True)
        self.thread.start()

    def enable_trigger(self, enable, cam_idxs):
        self.connection.root.enable_trigger(enable, cam_idxs=cam_idxs)

    def snap_image(self, cam_idx):
        return np.array(self.connection.root.cams[cam_idx].snap_image())

    def retrieve_image(self, cam_idx):
        return np.array(self.connection.root.cams[cam_idx].retrieve_image())

    def reset_frame_ready(self, cam_idx):
        self.connection.root.cams[cam_idx].cam.reset_frame_ready()

    def wait_till_frame_ready(self, cam_idx):
        self.connection.root.cams[cam_idx].cam.wait_til_frame_ready()

    def record_background(self):
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
        self.parameters.background.value = None


class RemoteParameter:
    def __init__(self, parent, remote, name):
        self.remote = remote
        self.name = name
        self.parent = parent

    @property
    def value(self):
        return self.remote.value

    @value.setter
    def value(self, value):
        self.remote.value = value

    def change(self, function):
        self.parent.register_listener(self, function)

    def reset(self):
        self.remote.reset()

    @property
    def _start(self):
        return self.remote._start


class RemoteParameters:
    def __init__(self, remote, uuid):
        self.remote = remote
        self.uuid = uuid

        for name, param in remote.get_all_parameters():
            setattr(self, name, RemoteParameter(self, param, name))

        self._listeners = {}

        self.call_listeners()

    def __iter__(self):
        for name, param in self.remote.get_all_parameters():
            yield name, param.value

    def register_listener(self, param, function):
        self.remote.register_remote_listener(self.uuid, param.name)
        self._listeners.setdefault(param.name, [])
        self._listeners[param.name].append(function)

    def call_listeners(self, something=None):
        for param_name in self.remote.get_listener_queue(self.uuid):
            value = getattr(self, param_name).value

            for listener in self._listeners[param_name]:
                listener(value)

        QtCore.QTimer.singleShot(100, self.call_listeners)