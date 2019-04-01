import rpyc
import numpy as np
from time import sleep
from threading import Thread


class Connection:
    def connect(self):
        #print('not connecting')
        self.image_data = [np.array([[1,2], [3,4]])] * 3
        #return
        self.connection = rpyc.connect('gain.physik.hu-berlin.de', 8000)
        # FIXME: not using continuous mode
        # self.connection.root.start_continuous_mode()

    def run_acquisition_thread(self):
        def retrieve_data():
            while True:
                # FIXME: not using continuous mode
                """data = list(self.connection.root.continuous_camera_images)
                is_good_data = True
                for d in data:
                    if not d:
                        is_good_data = False

                if is_good_data:
                    self.image_data = list(self.connection.root.continuous_camera_images)"""
                for idx in range(3):
                    self.image_data[idx] = np.array(self.connection.root.cams[idx].snap_image())
                sleep(.05)

        self.thread = Thread(target = retrieve_data, args = tuple())
        self.thread.start()
        #thread.join()

    def set_exposure_time(self, exposure):
        for cam in self.connection.root.cams:
            cam.set_exposure(exposure)

    def enable_trigger(self, enable):
        self.connection.root.enable_trigger(enable)

    def snap_image(self, cam_idx):
        return np.array(self.connection.root.cams[cam_idx].snap_image())

    def retrieve_image(self, cam_idx):
        return np.array(self.connection.root.cams[cam_idx].retrieve_image())

    def reset_frame_ready(self, cam_idx):
        self.connection.root.cams[cam_idx].cam.reset_frame_ready()

    def wait_till_frame_ready(self, cam_idx):
        self.connection.root.cams[cam_idx].cam.wait_til_frame_ready()