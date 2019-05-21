"""
    gain_camera.parameters
    ~~~~~~~~~~~~~~~~~~~~~~

    Utils for storing and managing a set of parameters.
    `gain_camera.connection` contains utilities for accessing these parameters
    remotely.
"""
import rpyc
from time import sleep


class Parameter:
    """Represents a single parameter and is used by `Parameters`."""
    def __init__(self, min_=None, max_=None, start=None, wrap=False):
        self.min = min_
        self.max = max_
        self.wrap = wrap
        self._value = start
        self._start = start
        self._listeners = set()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        # check bounds
        if self.min is not None and value < self.min:
            value = self.min if not self.wrap else self.max
        if self.max is not None and value > self.max:
            value = self.max if not self.wrap else self.min

        self._value = value

        # we copy it because a listener could remove a listener --> this would
        # cause an error in this loop
        for listener in self._listeners.copy():
            listener(value)

    def change(self, function):
        self._listeners.add(function)

        if self._value is not None:
            function(self._value)

    def remove_listener(self, function):
        self._listeners.remove(function)

    def reset(self):
        self.value = self._start

    def register_remote_listener(self, remote_uuid):
        pass


class BaseParameters:
    """Represents a set of parameters.

    Parameters can be changed like this:

        p = Parameters(...)
        p.my_param.value = 123

    You can register callback functions like this:

        def on_change(value):
            # do something

        p.my_param.change(on_change)
    """
    def __init__(self):
        self._remote_listener_queue = {}
        self._remote_listener_callbacks = {}

    def get_all_parameters(self):
        for name, element in self.__dict__.items():
            if isinstance(element, Parameter):
                yield name, element

    def register_remote_listener(self, uuid, param_name, callback):
        self._remote_listener_queue.setdefault(uuid, set())
        self._remote_listener_callbacks.setdefault(uuid, [])

        def on_change(value, uuid=uuid, param_name=param_name, callback=callback):
            self._remote_listener_queue[uuid].add((callback, value))

        param = getattr(self, param_name)
        param.change(on_change)

        self._remote_listener_callbacks[uuid].append((param, on_change))

    def unregister_remote_listeners(self, uuid):
        for param, callback in self._remote_listener_callbacks:
            param.remove_listener(callback)

        del self._remote_listener_queue[uuid]
        del self._remote_listener_callbacks[uuid]

    def get_listener_queue(self, uuid):
        queue = self._remote_listener_queue.get(uuid, set())
        self._remote_listener_queue[uuid] = set()
        return queue

    def __iter__(self):
        for name, param in self.get_all_parameters():
            yield name, param.value

    def _get_param(self, param_name):
        param = getattr(self, param_name)
        assert isinstance(param, Parameter)
        return param


class BaseService(rpyc.Service):
    def __init__(self, parameter_cls):
        self.parameters = parameter_cls()
        self._uuid_mapping = {}

    def on_connect(self, client):
        # as long as the connection to the client exists, we will check for
        # parameter changes and send them to the client

        uuid = client.root.uuid
        self._uuid_mapping[client] = uuid

        while True:
            for callback, value in self.parameters.get_listener_queue(uuid):
                callback(value)

            sleep(.05)

    def on_disconnect(self, client):
        uuid = self._uuid_mapping[client]
        self.parameters.unregister_remote_listeners(uuid)