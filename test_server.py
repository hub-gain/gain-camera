import rpyc
from time import sleep
from rpyc.utils.server import ThreadedServer


class MyService(rpyc.Service):
    def on_connect(self, client):
        print('connect', client, dir(client))
        print('result', client.root.exposed_foo(12))

        fct = client.root.get_fct()

        i = 0
        while True:
            print(i)
            #client.root.exposed_wait_forever(i)
            fct(i)
            i += 1
            sleep(5)

    def on_disconnect(self, client):
        print('disconnect!')

    def exposed_foo(self):
        return 42

if __name__ == '__main__':
    server = ThreadedServer(MyService(), port=8000)
    server.start()