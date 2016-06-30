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
    if time() - lastSignal > 1:
        dyaw = 0
        pitch = 0
        newY = 0
    dt = time()-lastTime
    yaw += dyaw * dt * 150
    x += dt * 5 * pitch * sin(radians(yaw))
    z += dt * 5 * pitch * -cos(radians(yaw))
    if newY-y > 4 * dt:
        y += 4 * dt
    elif y-newY > 4 * dt:
        y -= 4 * dt
    else:
        y = newY
    lastTime = time()
    mc.entity.setRotation(pig, yaw)
    mc.entity.setPitch(pig, -30*pitch)
    mc.entity.setPos(pig, x,y,z)
    if remote.available():
        pitch = 0
        dyaw = 0
        event = remote.getevent()
        if event.format.startswith("HELI_"):
            extras = event.extras
            if extras:            
                pitch = extras.get('pitch', 0)
                dyaw = extras.get('yaw', 0) + extras.get('trim', 0)
                newY = extras.get('throttle', 0) * 40
                lastSignal = time()
    else:
        sleep(0.2)
    