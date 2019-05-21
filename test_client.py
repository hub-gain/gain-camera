import rpyc

class ClientService(rpyc.Service):
    def exposed_foo(self, value):
        print('received', value)
        return value + 1

    def exposed_get_fct(self):
        return self.wait_forever

    def wait_forever(self, i):
        from time import sleep
        print('wait!', i)
        sleep(1)


c = rpyc.connect('localhost', 8000, service=ClientService)
#bgsrv = rpyc.BgServingThread(c)

while True:
    from time import sleep
    sleep(.5)
    # this causes remote commands to be processed
    str(c.root)
    print('result', c.root.exposed_foo())