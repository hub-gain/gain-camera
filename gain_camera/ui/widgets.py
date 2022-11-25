import weakref
from pyqtgraph.Qt import QtCore, QtGui


class CustomWidget:
    instances = []

    def __init__(self, *args, **kwargs):
        self.__class__.instances.append(weakref.proxy(self))
        super().__init__(*args, **kwargs)

    def connection_established(self, connection):
        pass

    def get_widget(self, name):
        """Queries a widget by name."""
        return self.findChild(QtCore.QObject, name)
