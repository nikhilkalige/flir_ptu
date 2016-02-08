from ptu.ptu import PTU
import logging


logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s:%(name)s:- %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.setLevel(logging.DEBUG)

x = PTU("129.219.136.149", 4000)
x.connect()

value = 3

if value == 1:
    x.pan(25)
    print(x.pan())
elif value == 2:
    x.pan_angle(45)
    print(x.pan())
elif value == 3:
    x.pan_offset(-10)
    print("XX", x.pan())

x.stream.close()
