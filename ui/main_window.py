# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.cameras = CameraWidget(self.centralwidget)
        self.cameras.setObjectName("cameras")
        self.verticalLayout.addWidget(self.cameras)
        self.atom_numbers = AtomNumberWidget(self.centralwidget)
        self.atom_numbers.setObjectName("atom_numbers")
        self.verticalLayout.addWidget(self.atom_numbers)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.exposureTime = SelectExposureTimeWidget(self.groupBox_3)
        self.exposureTime.setObjectName("exposureTime")
        self.verticalLayout_4.addWidget(self.exposureTime)
        self.verticalLayout_2.addWidget(self.groupBox_3)
        self.recordBackgroundBox = RecordBackgroundBox(self.centralwidget)
        self.recordBackgroundBox.setObjectName("recordBackgroundBox")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.recordBackgroundBox)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.recordBackground = QtWidgets.QPushButton(self.recordBackgroundBox)
        self.recordBackground.setObjectName("recordBackground")
        self.verticalLayout_3.addWidget(self.recordBackground)
        self.clearBackground = QtWidgets.QPushButton(self.recordBackgroundBox)
        self.clearBackground.setObjectName("clearBackground")
        self.verticalLayout_3.addWidget(self.clearBackground)
        self.verticalLayout_2.addWidget(self.recordBackgroundBox)
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.checkBox = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkBox.setObjectName("checkBox")
        self.verticalLayout_5.addWidget(self.checkBox)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.spinBox = QtWidgets.QSpinBox(self.groupBox_2)
        self.spinBox.setObjectName("spinBox")
        self.gridLayout.addWidget(self.spinBox, 1, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox_2)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.spinBox_2 = QtWidgets.QSpinBox(self.groupBox_2)
        self.spinBox_2.setObjectName("spinBox_2")
        self.gridLayout.addWidget(self.spinBox_2, 0, 1, 1, 1)
        self.spinBox_3 = QtWidgets.QSpinBox(self.groupBox_2)
        self.spinBox_3.setObjectName("spinBox_3")
        self.gridLayout.addWidget(self.spinBox_3, 0, 2, 1, 1)
        self.spinBox_4 = QtWidgets.QSpinBox(self.groupBox_2)
        self.spinBox_4.setObjectName("spinBox_4")
        self.gridLayout.addWidget(self.spinBox_4, 1, 2, 1, 1)
        self.verticalLayout_5.addLayout(self.gridLayout)
        self.verticalLayout_2.addWidget(self.groupBox_2)
        self.groupBox_4 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_4.setObjectName("groupBox_4")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.groupBox_4)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.checkBox_2 = QtWidgets.QCheckBox(self.groupBox_4)
        self.checkBox_2.setObjectName("checkBox_2")
        self.verticalLayout_6.addWidget(self.checkBox_2)
        self.checkBox_3 = QtWidgets.QCheckBox(self.groupBox_4)
        self.checkBox_3.setObjectName("checkBox_3")
        self.verticalLayout_6.addWidget(self.checkBox_3)
        self.verticalLayout_2.addWidget(self.groupBox_4)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupBox_3.setTitle(_translate("MainWindow", "Exposure time"))
        self.recordBackgroundBox.setTitle(_translate("MainWindow", "Background"))
        self.recordBackground.setText(_translate("MainWindow", "Record background"))
        self.clearBackground.setText(_translate("MainWindow", "Clear background"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Crop"))
        self.checkBox.setText(_translate("MainWindow", "enable"))
        self.label_2.setText(_translate("MainWindow", "x"))
        self.label.setText(_translate("MainWindow", "y"))
        self.groupBox_4.setTitle(_translate("MainWindow", "Atom number"))
        self.checkBox_2.setText(_translate("MainWindow", "record"))
        self.checkBox_3.setText(_translate("MainWindow", "wait for trigger"))

from atom_number_widget import AtomNumberWidget
from camera_widget import CameraWidget
from record_background_box import RecordBackgroundBox
from select_exposure_time import SelectExposureTimeWidget

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

