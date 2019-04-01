import os
import dill
import rpyc
import numpy as np
from threading import Thread, Pipe

os.chdir('C:\\Users\\gain\\Documents\\The Imaging Source Europe GmbH\\TIS Grabber DLL\\bin\\win32')
import icpy3

from time import time
from matplotlib import pyplot as plt
from rpyc.utils.server import ThreadedServer

from utils import img2count, crop_imgs
from parameters import Parameters


class Camera:
    def __init__(self, ic, idx):
        filename = 'camera%d' % idx
        try:
            cam = ic.get_device_by_file(filename)
            cam.exposure.value
        except:
            print('opening camera %d' % idx)
            cam = ic.get_device_by_dialog()
            cam.save_device_state(filename)

        #cam.exposure.value = -13
        cam.exposure.value = -3
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
        img = np.ndarray(buffer = d, dtype = np.uint8, shape = (img_width, img_height, img_depth))
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

        #cam.set_format(0)
        #cam.snap_image()

        """input('ready for calibration?')"""
        """for cam in cams:
            cam.calibrate()"""


        """for cam in cams:
            cam.cam.enable_continuous_mode(True)

        for i in range(3):
            # for some strange reason this does not work when inside Camera class
            cams[i].cam.start_live()
            if not cams[i].cam.callback_registered:
                cams[i].cam.register_frame_ready_callback()

            cams[i].cam.enable_trigger(True)"""

    def _register_listeners(self):
        def change_exposure(exposure):
            for cam in self.cams:
                cam.set_exposure(exposure)
        self.parameters.exposure.change(change_exposure)

    def start_continuous_mode(self):
        if self.acquisition_thread is not None:
            return

        def do(child_pipe):
            while not child_pipe.poll():
                for idx, cam in self.cams:
                    self.continuous_camera_images[idx] = np.array(cam.snap_image())

        pipe, child_pipe = Pipe()

        self.acquisition_thread = Thread(target = do, args = (child_pipe,))
        self.acquisition_thread.start()
        self.acquisition_thread_pipe = pipe

    def stop_continuous_mode(self):
        self.acquisition_thread = None
        self.acquisition_thread_pipe.send(True)
        self.acquisition_thread_pipe = None

    def record_background(self):
        exposures = np.arange(-2, -13.1, -1)
        backgrounds = []

        for idx, exposure in enumerate(exposures):
            for cam in self.cams:
                cam.set_exposure(exposure)
                cam.snap_image()

            backgrounds.append(
                [cam.snap_image() for cam in self.cams]
            )

        self.parameters.background.value = backgrounds

    def record_series(self):
        cams = self.cams
        for cam in cams:
            cam.cam.enable_continuous_mode(True)

        for i in range(3):
            # for some strange reason this does not work when inside Camera class
            cams[i].cam.start_live()
            if not cams[i].cam.callback_registered:
                cams[i].cam.register_frame_ready_callback()

            cams[i].cam.enable_trigger(True)

        SMOT = 0
        MOT = 1

        cams = self.cams
        for cam in cams:
            cam.cam.reset_frame_ready()

        d = {}
        last_time = time()
        times = []
        atom_numbers = []

        for j in [SMOT, MOT]:
            print('SMOT' if j == SMOT else 'MOT')
            for img_number in range(10000000):
                print('n', img_number)

                imgs = []

                for cam in cams:
                    cam.cam.wait_til_frame_ready()
                    imgs.append(cam.retrieve_image())

                new_time = time()
                times.append(new_time)

                for cam in cams:
                    # this is necessary for all cams in order to flush img cache
                    cam.cam.reset_frame_ready()

                atom_number = np.mean([img2count(img, cam.cam.exposure.value) for img, cam in zip(imgs, cams)])
                atom_numbers.append(atom_number)

                if new_time - last_time > 1 and img_number > 0:
                    #for img in imgs:
                    #    plt.pcolormesh(img)
                    #    plt.show()
                    if j == SMOT:
                        d['N_smot'] = atom_number
                        d['img_smot_live'] = crop_imgs(last_imgs)
                        d['img_smot_after'] = crop_imgs(imgs)
                    else:
                        d['N_mot'] = atom_number
                        d['img_mot'] = crop_imgs(imgs)

                    break

                last_time = new_time
                last_imgs = imgs

        times = [_ - times[0] for _ in times]
        #plt.plot(times, atom_numbers)
        #plt.grid()
        #plt.show()

        d.update({
            'times': times,
            'atom_numbers': atom_numbers,
        })

        #data.append(d)

        #plt.plot([_['N_smot'] for _ in data])
        #plt.plot([_['N_mot'] for _ in data])
        #plt.grid()
        #plt.show()
        return d

    def enable_trigger(self, enable):
        if enable:
            for cam in self.cams:
                try:
                    cam.cam.suspend_live()
                except:
                    pass

            for cam in self.cams:
                cam.cam.enable_continuous_mode(True)

            for cam in self.cams:
                cam.cam.start_live()
                if not cam.cam.callback_registered:
                    cam.cam.register_frame_ready_callback()
                cam.cam.enable_trigger(True)
        else:
            for cam in self.cams:
                cam.cam.enable_trigger(False)


if __name__ == '__main__':
    server = ThreadedServer(CameraService, port=8000, protocol_config={
        'allow_public_attrs': True,
        'allow_pickle': True
    })
    server.start()
