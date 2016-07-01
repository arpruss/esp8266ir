# public domain by Alexander Pruss

import socket
import StringIO
import select

class ESPRemoteEvent(object):
    def __init__(self, line):
        parts = line.strip().split(" ")
        if parts[0] == "OK":
            self.format = "IGNORE"
            self.time = 0
            self.bits = 0
            self.data = 0
            self.extras = {}
            self.raw = None
            return
        line = parts[0]
        try:
            d = line.strip().split(",")
            self.format = d[0]
        except:
            self.format = ""
        try:
            self.time = long(d[1])
        except:
            self.time = 0
        try:
            self.bits = int(d[2])
        except:
            self.bits = 0
        try:
            if self.bits > 31:
                self.data = long(d[3], 16)
            else:
                self.data = int(d[3], 16)
        except:
            self.data = 0
        self.extras = {}
        for entry in d[4:]:
            try:
                label,stringValue = entry.split("=")
                self.extras[label] = ESPRemoteEvent.number(stringValue)
            except:
                pass
        if self.format.startswith("HELI_"):
            self.setupHeli()
        self.raw = None        
        if len(parts)>1 and parts[1][0] == "[" and parts[1][-1] == "]":
            self.raw = map(int, parts[1][1:-2].split(","))
            
    @staticmethod
    def trim(x):
        if x <= -1.: return -1.
        elif x >= 1.: return 1.
        else: return x
            
    # pitch: positive = nose up, heli backward  
    # yaw/trim: positive = right    
    def setupHeli(self):
        if self.format == "HELI_SYMA_R3" or self.format == "HELI_SYMA_R5":
            self.extras['throttle'] = ESPRemoteEvent.trim(self.extras.get('throttle', 0) / 127.)
            self.extras['pitch'] = ESPRemoteEvent.trim((self.extras.get('pitch', 0) - 63.)/63.)
            self.extras['yaw'] = ESPRemoteEvent.trim((63. - self.extras.get('yaw',0))/63.)
            if self.format == "HELI_SYMA_R5":
                self.extras['trim'] = ESPRemoteEvent.trim((63. - self.extras.get('trim',0))/63.)
            else:
                self.extras['trim'] = 0
        elif self.format == "HELI_FAKE_SYMA1":
            self.extras['throttle'] = ESPRemoteEvent.trim(self.extras.get('throttle', 0) / 127.)
            self.extras['pitch'] = ESPRemoteEvent.trim(self.extras.get('pitch',0) / 7.)
            if self.extras.get('pitchdir', 0): 
                self.extras['pitch'] = -self.extras['pitch']
            self.extras['yaw'] = ESPRemoteEvent.trim(self.extras.get('yaw',0) / 15.)
            if self.extras.get('yawdir', 0): 
                self.extras['yaw'] = -self.extras['yaw']
            self.extras['trim'] = ESPRemoteEvent.trim(self.extras.get('trim',0) / 15.)
            if self.extras.get('trimdir', 0): 
                self.extras['trim'] = -self.extras['trim']
            try:
                del self.extras['pitchdir']
            except:
                pass
            try:
                del self.extras['trimdir']
            except:
                pass
            try:
                del self.extras['yawdir']
            except:
                pass
        elif self.format == "HELI_FASTLANE":
            self.extras['throttle'] = ESPRemoteEvent.trim(self.extras.get('throttle', 0) / 63.)
            self.extras['pitch'] = ESPRemoteEvent.trim((8. - self.extras.get('pitch', 0)) / 7.)
            self.extras['yaw'] = ESPRemoteEvent.trim((8. - self.extras.get('yaw',0))/7.)
            self.extras['trim'] = ESPRemoteEvent.trim((8. - self.extras.get('trim',0))/7.)
        elif self.format == 'HELI_USERIES':
            self.extras['throttle'] = ESPRemoteEvent.trim(self.extras.get('throttle', 0) / 127.)
            self.extras['pitch'] = ESPRemoteEvent.trim((self.extras.get('pitch', 0) - 31.) / 31.)
            self.extras['yaw'] = ESPRemoteEvent.trim((15. - self.extras.get('yaw',0))/15.)
            self.extras['trim'] = ESPRemoteEvent.trim((31. - self.extras.get('trim',0))/31.)
        else: # unknown
            self.extras['throttle'] = 0
            self.extras['pitch'] = 0
            self.extras['yaw'] = 0
            self.extras['trim'] = 0

    def __str__(self):
        out = "format=%s time=%d bits=%d data=%x" % (self.format, self.time, self.bits, self.data)
        if len(self.extras):
            out += " extras: "+str(self.extras)
        if self.raw:
            out += " raw:"
            for i,r in enumerate(self.raw):
                out += "\t+" if i%2 else "\t-"
                out += str(r)
        return out
        
    @staticmethod
    def number(s):
        try:
            xl = long(s)
            xi = int(s)
            if xl == xi:
                return xi
            else:
                return xl
        except:
            return 0

class ESPRemote(object):
    def __init__(self, address="192.168.1.123", port=5678):
        self.address = address
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((address, port))
        if not self.readline().startswith("IRToWebThingy"):
            raise Exception("Invalid IRToWebThingy")
            
    def readline(self):
        b = StringIO.StringIO(1024)
        while True:
            d = self.sock.recv(1)
            if d:
                b.write(d)
            if d == "\n" or not d:
                return b.getvalue()
                
    def getevent(self):
        l = self.readline()
        if l:
            return ESPRemoteEvent(l)
        else:
            return None
                
    def getevents(self):
        while True:
            e = self.getevent()
            if not e:
                self.close()
                return
            yield e
                
    def available(self):
        return bool(select.select([self.sock], [], [], 0.0)[0])
        
    def setraw(self, v):
        self.sock.send("raw "+("1" if v else "0")+"\n")

    def setunknown(self, v):
        self.sock.send("unknown "+("1" if v else "0")+"\n")

    def close(self):
        self.sock.close()
        
if __name__=="__main__":
    from sys import argv

    if len(argv) > 1 and not argv[len(argv) - 1].startswith("-"):
        r = ESPRemote(argv[len(argv) - 1])
    else:
        r = ESPRemote()
    
    print "Thingy on "+str(r.address)+":"+str(r.port)

    for i in range(1,len(argv)):
        if argv[i] == "--raw" or argv[i] == "-raw":
            r.setraw(True)
        elif argv[i] == "--noraw" or argv[i] == "-noraw":
            r.setraw(False)
        elif argv[i] == "--unknown" or argv[i] == "-unknown":
            r.setunknown(True)
        elif argv[i] == "--nounknown" or argv[i] == "-nounknown":
            r.setunknown(False)
    
    for e in r.getevents():
        print e
        