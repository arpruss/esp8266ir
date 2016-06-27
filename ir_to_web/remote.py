import win32com.client
import win32api, win32con, win32gui
from espremote import ESPRemote

shell = win32com.client.Dispatch("WScript.Shell")
shell.AppActivate("Chrome")

width = win32api.GetSystemMetrics(0)
height = win32api.GetSystemMetrics(1)
    
lastTime = 0

for event in ESPRemote().getevents():
    title=win32gui.GetWindowText(win32gui.GetForegroundWindow())
    repeat = event.time < lastTime + 500
    
    data = event.data & 0xFFF
    
    if data == 0x42c:
        if not repeat:
            if title.startswith("Acorn"):
                win32api.SetCursorPos((500,500))
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 500,500, 0, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,  500,500, 0, 0)
                win32api.SetCursorPos((width-1,500))
            else: #if title.startswith("Netflix"):
                shell.SendKeys(" ")
    elif data == 0x458:
        shell.SendKeys("\xAF")
    elif data == 0x459:
        shell.SendKeys("\xAE")
    elif data == 0x40C:
        exit()
    else:
        print hex(event.data)
    lastTime = event.time 

#shell.SendKeys("^a") # CTRL+A may "select all" depending on which window's focused
#shell.SendKeys("{DELETE}") # Delete selected text?  Depends on context. :P
#shell.SendKeys("{TAB}") #Press tab... to change focus or whatever
