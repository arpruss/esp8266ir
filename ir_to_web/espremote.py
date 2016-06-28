# public domain by Alexander Pruss

import socket
import StringIO
import select


class ESPRemoteEvent(object):
    def __init__(self, line):
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

    def __str__(self):
        out = "format=%s time=%d bits=%d data=%x" % (self.format, self.time, self.bits, self.data)
        if len(self.extras):
            out += " extras: "+str(self.extras)
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

    def close(self):
        self.sock.close()
        
if __name__=="__main__":
    r = ESPRemote()
    print "Thingy on "+str(r.address)+":"+str(r.port)
    for e in r.getevents():
        print str(e)
        