from flir.stream import Stream
from flir.flir import FLIR
import time


#h = Stream("129.219.136.149", 4000)
#h.connect()
#time.sleep(5)
#h.write("PP-500".encode("ascii"))

x = FLIR("129.219.136.149", 4000)
x.connect()

value = True
#value = False

if value:
    x.pan(0)
    print(x.pan())
else:
    x.pan_angle(45)
    print(x.pan())
x.stream.close()
