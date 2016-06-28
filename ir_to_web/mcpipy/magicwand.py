
# Needs an IR to web thingy
#

from mc import *
from mcturtle import *
from espremote import *

r = ESPRemote()

mc = Minecraft()

lastEvent = -10000

for e in r.getevents():
    if e.time < lastEvent + 500:
        next
    lastEvent = e.time
    if e.format == "MAGIQUEST":
        radius = 15
        material = DIAMOND_BLOCK
    else:
        radius = 5
        material = GOLD_BLOCK
    t = Turtle(mc)
    t.penwidth(2*radius)
    t.penblock(material)
    t.go(0)
    t.pitch(90)
    t.penup()
    t.go(radius+2)
    t.pitch(-90)
        