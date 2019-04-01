class Parameter:
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


class Parameters:
    def __init__(self):
        self.exposure = Parameter(min_=-13, max_=-2, start=-2)
        self.background = Parameter()
        self.crop_enabled = Parameter(start=True)
        self.crop = Parameter(start=(0, 744, 0, 480))
        self.live_imgs = Parameter()
        self.trigger = Parameter(start=False)
        self.continuous_acquisition = Parameter(start=False)

        self._remote_listener_queue = {}

    def get_all_parameters(self):
        for name, element in self.__dict__.items():
            if isinstance(element, Parameter):
                yield name, element

    def register_remote_listener(self, uuid, param_name):
        self._remote_listener_queue.setdefault(uuid, set())

        def on_change(value, uuid=uuid, param_name=param_name):
            self._remote_listener_queue[uuid].add(param_name)

        param = getattr(self, param_name)
        param.change(on_change)

    def get_listener_queue(self, uuid):
        queue = self._remote_listener_queue.get(uuid, set())
        self._remote_listener_queue[uuid] = set()
        return queue

    def __iter__(self):
        for name, param in self.get_all_parameters():
            yield name, param.value