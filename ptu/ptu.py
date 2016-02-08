# -*- coding: utf-8 -*-
import re
import time
import math
from ptu.stream import Stream
import logging


logger = logging.getLogger('ptu.ptu')


cmds = {
    "pan": {
        "set": [lambda pos: "pp" + str(pos), True, False],
        "get": ["pp",
                r"\sCurrent Pan position is (?P<expected>\d+)\r\n"
                ]
    },
    "tilt": {
        "set": [lambda pos: "tp" + str(pos), True, False],
        "get": ["tp",
                r"\sCurrent Tilt position is (?P<expected>\d+)\r\n"
                ]
    },
    "pan_offset": {
        "set": [lambda pos: "po" + str(pos),
                True,
                lambda self, pos: int(self.pan()) + pos
                ],
        "get": ["po",
                r"\sTarget Pan position is (?P<expected>\d+)\r\n"
                ]
    },
    "tilt_offset": {
        "set": [lambda pos: "to" + str(pos),
                True,
                lambda self, pos: int(self.tilt()) + pos
                ],
        "get": ["to",
                r"\sTarget Tilt position is (?P<expected>\d+)\r\n"
                ]
    }
}


def position_decorator(cls):
    def generate_functions(cls, item, key):
        if item.get("get"):
            getter_valid = True
            read_string, regex = item["get"]
        else:
            getter_valid = False

        if item.get("set"):
            send_string, wait_completion, value_mod_func = item["set"]

        def template(self, *args):
            if len(args):
                cmd = send_string(*args)
                logger.info("Send command: ", cmd)
                self.send_command(send_string(*args))
                if wait_completion:
                    func = getattr(self, key)
                    if value_mod_func:
                        checking_value = value_mod_func(self, *args)
                    else:
                        checking_value = args[0]
                    while True:
                        value = func()
                        logger.debug("Read value wait: ", value)
                        if int(value) != checking_value:
                            time.sleep(.1)
                        else:
                            break
            else:
                if getter_valid:
                    return self.read_command(read_string, regex)
                else:
                    logger.warning("No valid getter command for ", key)

        setattr(cls, key, template)

    for key in cmds:
        item = cmds[key]
        generate_functions(cls, item, key)
    return cls


@position_decorator
class PTU:

    def __init__(self, host, port, debug=False):
        self.stream = Stream(host, port, testing=debug)

    def connect(self):
        self.stream.connect()

    def send_command(self, command):
        self.stream.send(command)
        print(self.stream.read_until("*"))

    def read_command(self, command, regex):
        self.stream.send(command)
        data = self.stream.read_until("*").decode()
        print(data)
        data = self.stream.read_until("\n").decode()
        print(data)
        match = re.match(regex, data)
        if match:
            return match.group("expected")
        else:
            logger.error("Error parsing regex")

    def pan_angle(self, angle_value=False):
        if angle_value:
            self.pan(math.ceil(angle_value/(92.5714/3600)))
        else:
            data = self.pan()
            return data * (92.5714/3600)

    def tile_angle(self, angle_value=False):
        if angle_value:
            self.pan((angle_value/(46.2857/3600)))
        else:
            data = self.pan()
            return data * (46.2857/3600)
