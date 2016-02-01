# -*- coding: utf-8 -*-
import re
import time
from flir.stream import Stream


cmds = {
    "pan": {
        "set": [lambda pos: "pp" + str(pos), True],
        "get": ["pp",
                r"\sCurrent Pan position is (?P<expected>\d+)\r\n"
                ]
    },
    "tilt": {
        "set": [lambda pos: "tp" + str(pos), True],
        "get": ["tp",
                r"Current Tilt position is (?P<expected>\d+)\r\n"
                ]
    },
    "pan_offset": {
        "get": [lambda pos: "po" + str(pos), True]
    },
    "tilt_offset": {
        "get": [lambda pos: "to" + str(pos), True]
    }
}


def position_decorator(cls):
    def generate_functions(cls, item, key):
        if item.get("get"):
            getter_valid = True
            read_string, regex = item["get"]
        else:
            getter_valid = False

        send_string, wait_completion = item["set"]

        def template(self, *args):
            if len(args):
                cmd = send_string(*args)
                print("command", cmd)
                self.send_command(send_string(*args))
                if wait_completion:
                    func = getattr(self, key)
                    while func() != args[0]:
                        time.sleep(0.1)
            else:
                if getter_valid:
                    return self.read_command(read_string, regex)
                else:
                    print("No valid getter command")

        setattr(cls, key, template)

    for key in cmds:
        item = cmds[key]
        generate_functions(cls, item, key)
    return cls


@position_decorator
class FLIR:

    def __init__(self, host, port):
        self.stream = Stream(host, port, testing=False)

    def connect(self):
        self.stream.connect()
        # for line in self.stream.read():
        #    print(line)

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
            print("error")

    def pan_angle(self, angle_value=False):
        if angle_value:
            self.pan(angle_value/(92.5714/3600))
        else:
            data = self.pan()
            return data * (92.5714/3600)

    def tile_angle(self, angle_value=False):
        if angle_value:
            self.pan(angle_value/(46.2857/3600))
        else:
            data = self.pan()
            return data * (46.2857/3600)



class Position:

    def __init__(self, stream):
        self.stream = stream

    def pan(self, position=False):
        if position:
            self.stream.send("PP" + position)
        else:
            self.stream.send("PP")

    def tilt(self, position=False):
        if position:
            self.stream.send("TP" + position)
        else:
            self.stream.send("TP")

    def pan_offset(self):
        pass

    def tilt_offset(self):
        pass

    def pan_resolution(self):
        pass

    def tilt_resolution(self):
        pass

    def preset_set(self):
        pass

    def preset_goto(self):
        pass

    def preset_clear(self):
        pass

    def monitor(self):
        pass

    def monitor_auto_enable(self):
        pass

    def monitor_auto_disable(self):
        pass

    def monitor_auto_query(self):
        pass

    def monitor_status(self):
        pass

    def immediate_execution_mode(self):
        pass

    def slaved_mode(self):
        pass

    def halt_all(self):
        pass

    def halt_pan(self):
        pass

    def halt_tilt(self):
        pass
