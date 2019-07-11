"""
    gain_camera.camera_live_view
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A GUI for controlling the camera server.
"""
import os
import sys
import signal
import traceback
# add ui folder to path
sys.path += [
    os.path.join(*list(
        os.path.split(os.path.abspath(__file__))[:-1]) + ['ui']
    )
]
import numpy as np
import pyqtgraph as pg

from time import sleep
from matplotlib import pyplot as plt
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5 import QtWidgets

from gain_camera.connection import CameraConnection
from widgets import CustomWidget


class CameraApplication:
    def __init__(self, app, window):
        self.app = app
        self.window = window
        self.init()

        app.aboutToQuit.connect(self.shutdown)

    def init(self):
        self.connection = CameraConnection(
            'gain.physik.hu-berlin.de', 8000, keep_in_sync=True
        )
        self.connection.run_continuous_acquisition()

        self.draw_images()
        self.call_listeners()

        for instance in CustomWidget.instances:
            instance.connection_established(self.connection)

    def get_widget(self, name):
        """Queries a widget by name."""
        return self.window.findChild(QtCore.QObject, name)

    def draw_images(self):
        """This function is called periodically. It checks if there is any new
        image data. If yes, it updates the 2D plots and adds a data point to the
        atom number plot."""
        image_data = self.connection.image_data

        if image_data is not None:
            self.connection.image_data = None

            # check that it is a real image (may be undefined after startup)
            data_not_good = False
            for d in image_data:
                if d is None:
                    data_not_good = True

            if not data_not_good:
                # plot 2D images
                camera_widget = self.get_widget('cameras')
                camera_widget.draw_images(image_data)

        atom_number_data = self.connection.atom_number_data
        if atom_number_data:
            # add data point to atom number plot
            atom_number_widget = self.get_widget('atom_numbers')
            atom_number_widget.update(atom_number_data)

        # queue this function again
        QtCore.QTimer.singleShot(50, self.draw_images)

    def call_listeners(self):
        self.connection.parameters.call_listeners()
        QtCore.QTimer.singleShot(100, self.call_listeners)

    def shutdown(self):
        self.app.quit()


if __name__ == '__main__':
    from gain_camera.ui.main_window import Ui_MainWindow
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()

    persistent = {}
    def _run():
        while True:
            try:
                persistent['application'] = CameraApplication(app, MainWindow)
                break
            except:
                print('connection error')
                traceback.print_exc()
                sleep(1)

    QtCore.QTimer.singleShot(1, _run)

    # catch ctrl-c and shutdown
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    sys.exit(app.exec_())
