from mcturtle import *
from espremote import*
t=Turtle()
r=ESPRemote()
t.gridalign()
t.turtle(None)

while True:
    event=r.getevent()
    if event.data&0xfff==0x458:
        t.go(1)
    elif event.data&0xfff==0x459:
        t.go(-1)
    elif event.data&0xfff==0x45b:
        t.yaw(90)
        t.go(1)
        t.yaw(-90)
    elif event.data&0xfff==0x45a:
        t.yaw(-90)
        t.go(1)
        t.yaw(90)
    elif event.data&0xfff==0x45c:
        t.pitch(90)
        t.go(1)
        t.pitch(-90)
    elif event.data&0xfff==0x42c:
        t.pitch(-90)
        t.go(1)
        t.pitch(90)
    else:
        t.mc.postToChat(hex(event.data))
