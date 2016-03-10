# -*- coding: utf-8 -*-
from telnetlib import Telnet
from enum import IntEnum
import logging


logger = logging.getLogger(__name__)


class ConnectionState(IntEnum):
    INIT = 1
    CONNECTED = 2
    DISCONNECTED = 3


class Stream:

    def __init__(self, host, port, timeout=3000, testing=False):
        self.host = host
        self.port = port
        self.timeout = timeout

        self.socket = None
        self.testing = testing
        self.state = ConnectionState.INIT

    def connect(self):
        if self.testing:
            logger.debug("Connected")
            self.state = ConnectionState.CONNECTED
            return

        if self.state not in [ConnectionState.INIT or
                              ConnectionState.DISCONNECTED]:
            return

        try:
            self.socket = Telnet(self.host, self.port, self.timeout)
            data = self.socket.read_until(str.encode("*"))
            self.state = ConnectionState.CONNECTED
            logger.info(data)
        except OSError:
            logger.critical("Socket connection error")

    @property
    def is_connected(self):
        return self.state == ConnectionState.CONNECTED

    def ensure_connection(self):
        if self.is_connected:
            return
        raise OSError

    def close(self):
        if self.testing:
            logger.debug("Closed")
            return

        if not self.is_connected:
            return

        self.state = ConnectionState.DISCONNECTED
        self.socket.close()

    def send(self, cmd):
        logger.debug(cmd)
        if self.testing:
            return

        self.ensure_connection()
        try:
            self.socket.write(cmd.encode("ascii") + b'\n')
        except OSError:
            logger.error("Error sending data")

    def read(self):
        self.ensure_connection()
        while True:
            data = self.socket.read_eager()
            if len(data) == 0:
                break

            yield data

    def read_until(self, string):
        if self.testing:
            logger.debug("Reading")
            return

        self.ensure_connection()
        return self.socket.read_until(str.encode(string))
