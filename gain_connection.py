import rpyc
import numpy as np
from time import sleep
from threading import Thread


class Connection:
    def connect(self):
        print('not connecting')
        self.image_data = [np.array([[1,2], [3,4]])] * 3
        return
        self.connection = rpyc.connect('gain.physik.hu-berlin.de', 8000)
        self.connection.root.start_continuous_mode()

    def run_acquisition_thread(self):
        def retrieve_data():
            while True:
                self.image_data = list(self.connection.root.continuous_camera_images)
                sleep(.05)

        self.thread = Thread(target = retrieve_data, args = tuple())
        self.thread.start()
        #thread.join()

    def set_exposure_time(self, exposure):
        for cam in self.connection.root.cams:
            cam.set_exposure(exposure)

    def enable_trigger(self, enable):
        for cam in self.connection.root.cams:
            cam.enable_trigger(enable)

    def snap_image(self, cam_idx):
        return np.array(self.connection.root.cams[cam_idx].snap_image())

    def reset_frame_ready(self, cam_idx):
        self.connection.root.cams[cam_idx].cam.reset_frame_ready()