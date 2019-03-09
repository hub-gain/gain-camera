import rpyc
from matplotlib import pyplot as plt
import sys
import time
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph as pg

from threading import Thread
from time import sleep


class App(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)

        #### Create Gui Elements ###########
        self.mainbox = QtGui.QWidget()
        self.setCentralWidget(self.mainbox)
        self.mainbox.setLayout(QtGui.QVBoxLayout())

        self.canvas = pg.GraphicsLayoutWidget()
        self.mainbox.layout().addWidget(self.canvas)

        self.label = QtGui.QLabel()
        self.mainbox.layout().addWidget(self.label)

        self.views = []
        self.imgs = []

        for idx in range(3):
            view = self.canvas.addViewBox()
            view.setAspectLocked(True)
            view.setRange(QtCore.QRectF(0,0, 480, 744))

            #  image plot
            img = pg.ImageItem(border='w')
            view.addItem(img)

            self.views.append(view)
            self.imgs.append(img)

            if idx < 2:
                self.canvas.nextColumn()



        #### Set Data  #####################

        self.counter = 0
        self.fps = 0.
        self.lastupdate = time.time()

        self.connect_cameras()

        #### Start  #####################
        self._update()

    def connect_cameras(self):
        self.connection = rpyc.connect('gain.physik.hu-berlin.de', 8000)
        self.cams = self.connection.root.cams

        for cam in self.cams:
            cam.set_exposure(-3)

        self.image_data = [np.array([[1,2], [3,4]])] * 3

        self.thread = Thread(target = self.retrieve_data, args = tuple())
        self.thread.start()
        #thread.join()

    def retrieve_data(self):
        while True:
            for idx, cam in enumerate(self.cams):
                self.image_data[idx] = np.array(cam.snap_image())
                """print('MAX', np.max(np.max(self.image_data[idx])))
                plt.pcolormesh(self.image_data[idx])
                plt.colorbar()
                plt.show()"""

    def _update(self):
        for idx in range(3):
            data = self.image_data[idx]
            self.imgs[idx].setImage(data, levels=(0, 255))

        now = time.time()
        dt = (now-self.lastupdate)
        if dt <= 0:
            dt = 0.000000000001
        fps2 = 1.0 / dt
        self.lastupdate = now
        self.fps = self.fps * 0.9 + fps2 * 0.1
        tx = 'Mean Frame Rate:  {fps:.3f} FPS'.format(fps=self.fps )
        self.label.setText(tx)
        QtCore.QTimer.singleShot(1, self._update)
        self.counter += 1


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    thisapp = App()
    thisapp.show()
    sys.exit(app.exec_())
