from mc import *
from espremote import ESPRemote
from time import sleep,time
from sys import argv

mc = Minecraft()

if len(argv)>1 and argv[1] == 'me':
    x,y,z = mc.player.getPos()
    pig = mc.getPlayerId()
else:
    playerPos = mc.player.getPos()
    x,y,z = playerPos.x,playerPos.y,playerPos.z+1
    pig = mc.spawnEntity(PIG if len(argv)<=1 else argv[1], x,y,z, '{NoAI:1}')

remote = ESPRemote()

yaw = mc.entity.getRotation(pig)
pitch = 0
newY = y
dyaw = 0

lastTime = time()
lastSignal = -1000
while True:
    print y,newY
    if time() - lastSignal > 1:
        dyaw = 0
        pitch = 0
        newY = 0
    dt = time()-lastTime
    yaw -= dyaw * dt * 2.5
    x += dt * .1 * pitch * -sin(radians(yaw))
    z += dt * .1 * pitch * cos(radians(yaw))
    if newY-y > 4 * dt:
        y += 4 * dt
    elif y-newY > 4 * dt:
        y -= 4 * dt
    else:
        y = newY
    lastTime = time()
    mc.entity.setRotation(pig, yaw)
    mc.entity.setPitch(pig, pitch)
    mc.entity.setPos(pig, x,y,z)
    if remote.available():
        pitch = 0
        dyaw = 0
        event = remote.getevent()
        if event.format.startswith("SYMA"):
            extras = event.extras
            if extras:            
                throttle = extras.get('throttle',0)
                pitch = 63 - extras.get('pitch', 63)
                dyaw = extras.get('yaw', 63) + extras.get('trim', 63) - 2*63
                newY = throttle * 0.3
                lastSignal = time()
    else:
        sleep(0.2)
    