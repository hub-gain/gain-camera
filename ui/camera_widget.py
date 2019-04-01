import numpy as np
from PyQt5 import QtGui, QtWidgets
from widgets import CustomWidget
from pyqtgraph import GraphicsLayoutWidget
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg


class CameraWidget(GraphicsLayoutWidget, CustomWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.views = []
        self.imgs = []

        for idx in range(3):
            view = self.addViewBox()
            view.setAspectLocked(True)

            #  image plot
            img = pg.ImageItem(border='w')
            view.addItem(img)

            self.views.append(view)
            self.imgs.append(img)

            if idx < 2:
                self.nextColumn()

    def draw_images(self, image_data):
        for idx in range(3):
            data = np.array(image_data[idx])
            self.imgs[idx].setImage(data, levels=(0, 255))

    def connection_established(self, connection):
        params = connection.parameters
        crop_enabled = params.crop_enabled.value
        crop = params.crop.value

        if not crop_enabled:
            x0 = 0
            y0 = 0
            width = 480
            height = 744
        else:
            x0, x1, y0, y1 = crop
            width = x1 - x0
            height = y1 - y0

        for view in self.views:
            view.setRange(QtCore.QRectF(x0, y0, width, height))