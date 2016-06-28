from mc import *
from espremote import ESPRemote
from time import sleep,time
from sys import argv

mc = Minecraft()

if len(argv)>1 and argv[1] == 'player':
    x,y,z = mc.player.getPos()
    pig = mc.getPlayerId()
else:
    playerPos = mc.player.getPos()
    x,y,z = playerPos.x,playerPos.y,playerPos.z+1
    pig = mc.spawnEntity(PIG if len(argv)<=1 else argv[1], x,y,z, '{NoAI:1}')

yaw = mc.entity.getRotation(pig)
remote = ESPRemote()

lastTime = time()
while True:
    dt = time()-lastTime
    lastTime = time()
    if remote.available():
        pitch = 0
        dyaw = 0
        event = remote.getevent()
        if event.format.startswith("SYMA"):
            extras = event.extras
            if extras:            
                throttle = extras.get('throttle',0)
                pitch = 63 - extras.get('pitch', 63)
                dyaw = extras.get('yaw', 63) - 63 - (63 - extras.get('trim', 63))
                y = throttle * 0.1
        yaw -= dyaw * dt * 2.5
        x += dt * .1 * pitch * -sin(radians(yaw))
        z += dt * .1 * pitch * cos(radians(yaw))
        mc.entity.setRotation(pig, yaw)
        mc.entity.setPos(pig, x,y,z)
    else:
        sleep(0.25)
    