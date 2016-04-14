# -*- coding: utf-8 -*-
import re
import time
import math
from flir_ptu.stream import Stream
import logging


logger = logging.getLogger(__name__)

"""
The below are the config definitions that are used to autogenerate and add
commands to the ptu class.

The syntax for adding a new command to the ptu class is
    name_of_command(this will be the name of the function): {
        If you need a get, use the below.
        "get" : [command_used_to_read_value, r"regex"],
        Note:
            The regex used is expected to return a single name
            parameter named `expected` which will be the returned
            value.

        If you need a set, use the below.
        "set" : [function_send, wait, function_wait]
        Note:
            `function_send` is passed the values that are passed to function
            `self.name_of_command(args)` and it needs to return the command that
            should be sent.
            `wait` is boolean that is used to determine whether you need the function
            to block.
            `function_wait` is passed the class as the first argument and the args as
            the rest. The function should return the value that is used in conjuction with
            the get command to determine whether the ptu has finished the operation.
    }
"""

cmds = {
    "pan": {
        "set": [lambda pos: "pp" + str(pos), True, False],
        "get": ["pp",
                r"\sCurrent Pan position is (?P<expected>-?\d+)\r\n"
                ]
    },
    "tilt": {
        "set": [lambda pos: "tp" + str(pos), True, False],
        "get": ["tp",
                r"\sCurrent Tilt position is (?P<expected>-?\d+)\r\n"
                ]
    },
    "pan_offset": {
        "set": [lambda pos: "po" + str(pos),
                True,
                lambda self, pos: int(self.pan()) + pos
                ],
        "get": ["po",
                r"\sTarget Pan position is (?P<expected>-?\d+)\r\n"
                ]
    },
    "tilt_offset": {
        "set": [lambda pos: "to" + str(pos),
                True,
                lambda self, pos: int(self.tilt()) + pos
                ],
        "get": ["to",
                r"\sTarget Tilt position is (?P<expected>-?\d+)\r\n"
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
                logger.info("Send command: {}".format(cmd))
                self.send_command(send_string(*args))
                if wait_completion:
                    func = getattr(self, key)
                    if value_mod_func:
                        checking_value = value_mod_func(self, *args)
                    else:
                        checking_value = args[0]
                    logger.info("Blocking to get value: {}".format(checking_value))
                    while True:
                        value = func()
                        logger.debug("Value read: {}".format(value))
                        if int(value) != checking_value:
                            time.sleep(.1)
                        else:
                            break
            else:
                if getter_valid:
                    return self.read_command(read_string, regex)
                else:
                    logger.warning("No valid getter command for {}".format(key))

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
        self.stream.read_until("*")

    def read_command(self, command, regex):
        self.stream.send(command)
        data = self.stream.read_until("*").decode()
        data = self.stream.read_until("\n").decode()
        match = re.match(regex, data)
        if match:
            return match.group("expected")
        else:
            logger.error("Error parsing regex")

    def pan_angle(self, angle_value=False):
        if type(angle_value) !=  bool:
            self.pan(math.ceil(angle_value/(92.5714/3600)))
        else:
            data = self.pan()
            return data * (92.5714/3600)

    def tilt_angle(self, angle_value=False):
        if type(angle_value) != bool:
            self.tilt(math.ceil(angle_value/(46.2857/3600)))
        else:
            data = self.tilt()
            return data * (46.2857/3600)
