import os
import sys
# add ui folder to path
sys.path += [
    os.path.join(*list(
        os.path.split(os.path.abspath(__file__))[:-1]) + ['ui']
    )
]
import numpy as np
import pyqtgraph as pg

from matplotlib import pyplot as plt
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5 import QtWidgets

from gain_connection import Connection, FakeConnection
from widgets import CustomWidget


class CameraApplication:
    def __init__(self, app, window):
        self.app = app
        self.window = window
        self.init()

        app.aboutToQuit.connect(self.shutdown)

    def init(self):
        self.connection = Connection()

        self.atom_numbers = []

        self.connection.connect()
        self.connection.run_acquisition_thread()
        self.draw_images()

        for instance in CustomWidget.instances:
            instance.connection_established(self.connection)

    def get_widget(self, name):
        """Queries a widget by name."""
        return self.window.findChild(QtCore.QObject, name)

    def draw_images(self):
        image_data = self.connection.image_data
        if image_data is not None:
            self.connection.image_data = None

            data_not_good = False
            for d in image_data:
                if d is None:
                    data_not_good = True

            if not data_not_good:
                camera_widget = self.get_widget('cameras')
                camera_widget.draw_images(image_data)

                atom_number_widget = self.get_widget('atom_numbers')
                atom_number_widget.update(image_data)

        QtCore.QTimer.singleShot(50, self.draw_images)

    def shutdown(self):
        self.app.quit()


if __name__ == '__main__':
    from ui.main_window import Ui_MainWindow
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    persistent = {}
    def _run():
        persistent['application'] = CameraApplication(app, MainWindow)

    QtCore.QTimer.singleShot(1, _run)

    sys.exit(app.exec_())
