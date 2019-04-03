import os
os.chdir('C:\\Users\\gain\\Documents\\The Imaging Source Europe GmbH\\TIS Grabber DLL\\bin\\win32')

import rpyc
import icpy3
import numpy as np
import msgpack
import msgpack_numpy as m
m.patch()

from time import time, sleep
from threading import Thread
from matplotlib import pyplot as plt
from multiprocessing import Pipe
from rpyc.utils.server import ThreadedServer

from gain_camera.utils import img2count, crop_imgs, EXPOSURES
from gain_camera.parameters import Parameters


MSG_STOP = 0
MSG_TRIGGER_ON = 1
MSG_TRIGGER_OFF = 2


class Camera:
    def __init__(self, ic, idx):
        # FIXME: GIT!
        folder = os.path.join(*os.path.split(
            os.path.abspath(__file__)
        )[:-1])
        filename = os.path.join(folder, 'camera%d' % idx)

        try:
            cam = ic.get_device_by_file(filename)
            cam.exposure.value
            print('successfully loaded camera config from %s' % filename)
        except:
            print('failed to load camera config from %s' % filename)
            print('opening camera dialog for cam %d' % idx)
            cam = ic.get_device_by_dialog()
            cam.save_device_state(filename)

        cam.prepare_live()
        self.cam = cam

    def snap_image(self):
        self.cam.start_live()
        self.cam.snap_image()
        data = self.retrieve_image()
        self.cam.suspend_live()

        return data

    def retrieve_image(self):
        [d, img_height, img_width, img_depth] = self.cam.get_image_data()
        img_depth = int(img_depth)
        img = np.ndarray(buffer=d, dtype=np.uint8, shape=(img_width, img_height, img_depth))
        data = img[:,:,0].astype(np.int16)

        return data

    def save_image(self, filename):
        self.cam.save_image(filename, 0)

    def set_exposure(self, value):
        self.cam.exposure.value = value


class CameraService(rpyc.Service):
    def __init__(self):
        self.ic = icpy3.IC_ImagingControl()
        self.ic.init_library()
        self.cams = [Camera(self.ic, idx) for idx in range(3)]
        cams = self.cams

        for cam in cams:
            try:
                cam.cam.suspend_live()
            except:
                pass

        self.parameters = Parameters()

        self.acquisition_thread = None
        self.continuous_camera_images = [[], [], []]

        self._register_listeners()

    def _register_listeners(self):
        """Listens to parameter changes and controls the camera accordingly."""
        def change_exposure(exposure):
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
        """Starts continuous acquisition mode.

        For this, a thread is started that continuously takes images,
        transmitting data via a pipe to the main thread."""
        if self.acquisition_thread is not None:
            print('continuous mode already started')
            return
        print('starting continuous mode')

        def do(child_pipe):
            for cam in self.cams:
                cam.cam.enable_continuous_mode(True)
                cam.cam.start_live(show_display=False)
                sleep(0.05)

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
                if should_stop:
                    break

                trigger = self.parameters.trigger.value
                if trigger:
                    no_trigger = False
                    for cam in self.cams:
                        if cam.cam.wait_til_frame_ready(500) == -1:
                            no_trigger = True
                            break
                    if no_trigger:
                        # no trigger received, let's try again in the next iteration
                        print('no trigger')
                        continue

                imgs = [np.array(self.retrieve_image(idx)) for idx, cam in enumerate(self.cams)]
                self.parameters.live_imgs.value  = msgpack.packb(imgs)

                if trigger:
                    reset = [cam.cam.reset_frame_ready() for cam in self.cams]
                else:
                    # FIXME: should this be removed? Optional? As parameter?
                    sleep(.1)

        pipe, child_pipe = Pipe()

        self.acquisition_thread = Thread(target = do, args = (child_pipe,))
        self.acquisition_thread.start()
        self.acquisition_thread_pipe = pipe

    def stop_continuous_acquisition(self):
        if self.acquisition_thread is not None:
            self.acquisition_thread = None
            self.acquisition_thread_pipe.send(MSG_STOP)

    def record_background(self):
        """Records a background image for all exposures that will be subtracted
        automatically for future images."""
        exposures = EXPOSURES
        backgrounds = []

        for cam in self.cams:
            try:
                cam.cam.suspend_live()
                cam.cam.enable_continuous_mode(False)
                print('suspend successful!')
            except:
                print('suspend failed')
                pass

        for idx, exposure in enumerate(exposures):
            for cam in self.cams:
                cam.set_exposure(int(exposure))
                cam.snap_image()

            backgrounds.append(
                [cam.snap_image() for cam in self.cams]
            )

        self.parameters.background.value = backgrounds

    def enable_trigger(self, enable, cam_idxs=None):
        if cam_idxs is None:
            cam_idxs = [0, 1, 2]
        cams = [self.cams[idx] for idx in cam_idxs]

        if enable:
            for cam in cams:
                try:
                    cam.cam.suspend_live()
                except:
                    print('suspend failed')
                    pass

            for cam in cams:
                cam.cam.enable_continuous_mode(True)
                sleep(.1)

                cam.cam.start_live()
                if not cam.cam.callback_registered:
                    cam.cam.register_frame_ready_callback()
                cam.cam.enable_trigger(True)
                sleep(.1)
        else:
            for cam in cams:
                cam.cam.enable_trigger(False)
                sleep(.1)

    def _subtract_background(self, img, idx):
        bg = self.parameters.background.value
        exposure = self.parameters.exposure.value
        exposure_idx = EXPOSURES.index(exposure)

        if bg is None:
            return img

        img = img - bg[exposure_idx][idx]
        img[img < 0] = 0
        return img

    def snap_image(self, idx):
        return self._subtract_background(self.cams[idx].snap_image(), idx)

    def retrieve_image(self, idx):
        return self._subtract_background(self.cams[idx].retrieve_image(), idx)


if __name__ == '__main__':
    # FIXME: security!
    server = ThreadedServer(CameraService(), port=8000, protocol_config={
        'allow_all_attrs': True,
        'allow_setattr': True,
        'allow_getattr': True,
        'allow_pickle': True
    })
    server.start()
