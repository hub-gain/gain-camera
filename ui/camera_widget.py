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
            view.setRange(QtCore.QRectF(0,0, 480, 744))

            #  image plot
            img = pg.ImageItem(border='w')
            view.addItem(img)

            self.views.append(view)
            self.imgs.append(img)

            if idx < 2:
                self.nextColumn()

    def draw_images(self, image_data):
        for idx in range(3):
            data = image_data[idx]
            self.imgs[idx].setImage(data, levels=(0, 255))
