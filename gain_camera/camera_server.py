"""
Starts a server that has exclusive access to the cameras. Multiple clients may connect
to this server.

Use `gain_camera.connection` to access it programmatically or call
`gain_camera.live_view` to open the camera GUI.
"""
import os
from pathlib import Path

package_root_folder = Path(__file__).parent

from multiprocessing import Pipe
from threading import Thread
from time import sleep

import msgpack
import msgpack_numpy
import numpy as np
from pyicic.IC_ImagingControl import IC_ImagingControl
from rpyc.utils.server import ThreadedServer

from .communication.server import BaseService
from .parameters import Parameters
from .utils import EXPOSURES, img2count

msgpack_numpy.patch()

MSG_STOP = 0
MSG_TRIGGER_ON = 1
MSG_TRIGGER_OFF = 2
MSG_CHANGE_EXPOSURE = 3


class Camera:
    """Low-level class for accessing a camera. Should not be used directly."""

    def __init__(self, idx):
        self.ic = IC_ImagingControl()
        self.ic.init_library()
        config_file = package_root_folder / "config" / f"camera{idx}"

        try:
            cam = self.ic.get_device_by_file(config_file)
            cam.exposure.value
            cam.exposure.value = -2
            print(f"Successfully loaded camera config from {config_file}.")
        except:
            print(f"Failed to load camera config from {config_file}.")
            print(f"Opening camera dialog for cam {idx}.")
            cam = self.ic.get_device_by_dialog()
            cam.save_device_state(config_file)

        cam.stop_live()

        cam.set_video_format("Y800 (744x480)")

        # this is very important! If the frame rate is higher than 15, accessing 3
        # cameras at the same time does not work!
        # See the comment at
        # https://www.theimagingsource.com/support/documentation/ic-imaging-control-cpp/meth_descGrabber_prepareLive.htm
        cam.set_frame_rate(10)

        cam.prepare_live()
        cam.enable_continuous_mode(True)
        cam.start_live(show_display=False)

        self.cam = cam

    def snap_image(self):
        self.cam.snap_image()
        data = self.retrieve_image()
        return data

    def retrieve_image(self):
        [d, img_height, img_width, img_depth] = self.cam.get_image_data()
        img_depth = int(img_depth)
        img = np.ndarray(
            buffer=d, dtype=np.uint8, shape=(img_width, img_height, img_depth)
        )
        data = img[:, :, 0].astype(np.int16)

        return data

    def save_image(self, filename):
        self.cam.save_image(filename, 0)

    def set_exposure(self, value):
        self.cam.exposure.value = value


class CameraControl(BaseService):
    def __init__(self):
        super().__init__(Parameters)

        self.cams = [Camera(idx) for idx in range(3)]

        self.acquisition_thread = None
        self.continuous_camera_images = [[], [], []]

        self._register_listeners()

    def _register_listeners(self):
        """Listens to parameter changes and controls the camera accordingly."""

        def change_exposure(exposure):
            if self.acquisition_thread is not None:
                # acquisition thread is running --> it should handle setting the
                # trigger (setting it directly may cause some problems).
                self.acquisition_thread_pipe.send(MSG_CHANGE_EXPOSURE)
            else:
                for cam in self.cams:
                    cam.set_exposure(exposure)

        self.parameters.exposure.change(change_exposure)

        def change_trigger(trigger):
            if self.acquisition_thread is not None:
                # acquisition thread is running --> it should handle setting the
                # trigger (setting it directly may cause some problems).
                self.acquisition_thread_pipe.send(
                    MSG_TRIGGER_ON if trigger else MSG_TRIGGER_OFF
                )
            else:
                self.enable_trigger(trigger)

        self.parameters.trigger.change(change_trigger)

        def continuous_acquisition(enable):
            if enable:
                self.start_continuous_acquisition()
            else:
                self.stop_continuous_acquisition()

        self.parameters.continuous_acquisition.change(continuous_acquisition)

    def start_continuous_acquisition(self):
        """
        Starts continuous acquisition mode.

        For this, a thread is started that continuously takes images, transmitting data
        via a pipe to the main thread.
        """

        if self.acquisition_thread is not None:
            print("continuous mode already started")
            return

        print("starting continuous mode")

        def do(child_pipe):
            while True:
                msgs = []
                while child_pipe.poll():
                    msgs.append(child_pipe.recv())

                should_stop = False
                for msg in msgs:
                    if msg == MSG_STOP:
                        should_stop = True
                    elif msg == MSG_TRIGGER_ON:
                        self.enable_trigger(True)
                    elif msg == MSG_TRIGGER_OFF:
                        self.enable_trigger(False)
                    elif msg == MSG_CHANGE_EXPOSURE:
                        exposure = self.parameters.exposure.value
                        for cam in self.cams:
                            cam.cam.exposure.value = exposure
                if should_stop:
                    break

                trigger = self.parameters.trigger.value
                if trigger:
                    all_were_triggered = True
                    for cam in self.cams:
                        if cam.cam.wait_til_frame_ready(500) == -1:
                            # no trigger received, let's try again in the next iteration
                            all_were_triggered = False
                            break

                    if not all_were_triggered:
                        print("no trigger")
                        continue

                imgs = []
                for idx, cam in enumerate(self.cams):
                    # msgpacking a list takes less bytes than msgpacking a
                    # numpy array
                    imgs.append(np.array(self._retrieve_image(idx)).tolist())

                self.parameters.live_imgs.value = msgpack.packb(imgs)

                # if recording is enabled, calculate the atom number
                if (
                    self.parameters.recording.value
                    and self.parameters.exposure.value is not None
                    and self.parameters.recording_length.value is not None
                ):
                    exposure = self.parameters.exposure.value
                    atoms = [img2count(data, exposure) for data in imgs]
                    self.parameters.live_atom_number.value = np.sum(atoms)
                elif self.parameters.live_atom_number.value is not None:
                    self.parameters.live_atom_number.value = None

                if trigger:
                    reset = [cam.cam.reset_frame_ready() for cam in self.cams]
                else:
                    sleep(0.05)

        pipe, child_pipe = Pipe()

        self.acquisition_thread = Thread(target=do, args=(child_pipe,))
        self.acquisition_thread.start()
        self.acquisition_thread_pipe = pipe

    def stop_continuous_acquisition(self):
        if self.acquisition_thread is not None:
            self.acquisition_thread = None
            self.acquisition_thread_pipe.send(MSG_STOP)

    def enable_trigger(self, enable, cam_idxs=None):
        if cam_idxs is None:
            cam_idxs = [0, 1, 2]
        cams = [self.cams[idx] for idx in cam_idxs]

        if enable:
            for cam in cams:
                if not cam.cam.callback_registered:
                    cam.cam.register_frame_ready_callback()
                cam.cam.enable_trigger(True)
        else:
            for cam in cams:
                cam.cam.enable_trigger(False)

    def _subtract_background(self, img, idx):
        bg = self.parameters.background.value
        exposure = self.parameters.exposure.value
        exposure_idx = EXPOSURES.index(exposure)

        if bg is None:
            return img

        img = img - bg[exposure_idx][idx]
        img[img < 0] = 0
        return img

    def _retrieve_image(self, idx, subtract=False):
        img = self.cams[idx].retrieve_image()
        if subtract:
            return self._subtract_background(img, idx)
        return img


class CameraAPIService(CameraControl):
    """
    Contains the public API of the camera server. Notice that you also may control some
    functionality by setting parameters.
    """

    def exposed_snap_image(self, idx, subtract=False):
        img = self.cams[idx].snap_image()
        if subtract:
            return self._subtract_background(img, idx)
        return img

    def exposed_retrieve_image(self, idx, subtract=False):
        return self._retrieve_image(idx, subtract=subtract)

    def exposed_reset_frame_ready(self, cam_idx):
        return self.cams[cam_idx].cam.reset_frame_ready()

    def exposed_wait_till_frame_ready(self, cam_idx):
        return self.cams[cam_idx].cam.wait_til_frame_ready()

    def exposed_record_background(self):
        """
        Records a background image for all exposures that will be subtracted
        automatically for future images.
        """
        exposures = EXPOSURES
        backgrounds = []

        self.enable_trigger(False)

        for idx, exposure in enumerate(exposures):
            print(exposure)
            for cam in self.cams:
                cam.set_exposure(int(exposure))

            sleep(0.5)

            backgrounds.append([cam.retrieve_image() for cam in self.cams])

        self.parameters.background.value = backgrounds

        if self.parameters.trigger.value:
            self.enable_trigger(True)

        for cam in self.cams:
            cam.set_exposure(self.parameters.exposure.value)


def main():
    server = ThreadedServer(CameraAPIService(), port=8000)
    server.start()


if __name__ == "__main__":
    main()
