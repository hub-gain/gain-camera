"""
    gain_camera.connection
    ~~~~~~~~~~~~~~~~~~~~~~

    Contains the client that can be used to access a camera server.
"""
import rpyc
import uuid
from gain_camera.communication.remote_parameters import RemoteParameters


class ClientService(rpyc.Service):
    def __init__(self, uuid):
        super().__init__()

        self.exposed_uuid = uuid


class BaseClient:
    def __init__(self, server, port):
        self.uuid = uuid.uuid4().hex

        self.client_service = ClientService(self.uuid)

        self.connection = rpyc.connect(server, port, service=self.client_service)
        self.parameters = RemoteParameters(
            self.connection.root,
            self.uuid
        )