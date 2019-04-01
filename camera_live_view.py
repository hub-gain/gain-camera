import os
import sys
# add ui folder to path
sys.path += [
    os.path.join(*list(
        os.path.split(os.path.abspath(__file__))[:-1]) + ['ui']#
    )
]
import numpy as np
import pyqtgraph as pg

from matplotlib import pyplot as plt
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5 import QtWidgets

from gain_connection import Connection, FakeConnection
from utils import img2count
from widgets import CustomWidget


class CameraApplication:
    def __init__(self, app):
        self.app = app
        self.init()

    def init(self):
        if not self.application_is_ready():
            print('app not yet ready')
            QtCore.QTimer.singleShot(100, self.init)
            return

        self.connection = FakeConnection()

        #### Create Gui Elements ###########

        self.atom_numbers = []

        #### Start  #####################
        self.connection.connect()
        self.connection.run_acquisition_thread()
        self.draw_images()

        for instance in CustomWidget.instances:
            instance.connection_established(self.connection)

    def get_widget(self, name):
        """Queries a widget by name."""
        return self.app.activeWindow().findChild(QtCore.QObject, name)

    def application_is_ready(self):
        return self.app.activeWindow() is not None

    def draw_images(self):
        image_data = list(self.connection.image_data)

        camera_widget = self.get_widget('cameras')
        camera_widget.draw_images(image_data)

        atom_number_widget = self.get_widget('atom_numbers')
        exposure = self.connection.parameters.exposure.value
        atoms = [
            img2count(data, exposure) for data in image_data
        ]
        atoms = np.sum(atoms)

        last = 0
        if len(self.atom_numbers) > 0:
            last = self.atom_numbers[-1]
        if atoms != last:
            # FIXME: Better!
            self.atom_numbers.append(atoms)

        self.atom_numbers = self.atom_numbers[-400:]
        atom_number_widget.draw(self.atom_numbers)

        # FIXME: this is not very resource friendly!
        QtCore.QTimer.singleShot(1, self.draw_images)


if __name__ == '__main__':
    from ui.main_window import Ui_MainWindow
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    persistent = {}
    def _run():
        persistent['application'] = CameraApplication(app)

    QtCore.QTimer.singleShot(1, _run)

    sys.exit(app.exec_())
