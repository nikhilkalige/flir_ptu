# -*- coding: utf-8 -*-
from telnetlib import Telnet
from enum import IntEnum


class ConnectionState(IntEnum):
    INIT = 1
    CONNECTED = 2
    DISCONNECTED = 3


class Stream:

    def __init__(self, host, port, timeout=3000):
        self.host = host
        self.port = port
        self.timeout = timeout

        self.socket = None
        self.state = ConnectionState.INIT

    def connect(self):
        if self.state not in [ConnectionState.INIT or
                              ConnectionState.DISCONNECTED]:
            return

        try:
            self.socket = Telnet(self.host, self.port, self.timeout)
        except OSError:
            print("socket connection error")

    @property
    def is_connected(self):
        return self.state == ConnectionState.CONNECTED

    def ensure_connection(self):
        if self.is_connected:
            return
        raise OSError

    def close(self):
        if not self.is_connected:
            return

        self.state = ConnectionState.DISCONNECTED
        self.socket.close()

    def send(self, cmd):
        self.ensure_connection()
        try:
            self.socket.write(cmd.encode("ascii") + b'\n')
        except OSError:
            print("Error sending data")

    def read(self):
        self.ensure_connection()
        while True:
            data = self.socket.read_eager()
            if len(data) == 0:
                break

            yield data
