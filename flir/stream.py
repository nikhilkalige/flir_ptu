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
