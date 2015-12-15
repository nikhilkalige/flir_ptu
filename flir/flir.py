# -*- coding: utf-8 -*-
from flir.stream import Stream


class FLIR:

    def __init__(self, host, port):
        self.stream = Stream(host, port)

    def connect(self):
        self.stream.connect()
        for line in self.stream.read():
            print line





