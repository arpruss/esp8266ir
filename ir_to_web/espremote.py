# public domain by Alexander Pruss

import socket
import StringIO
import select

class ESPRemote(object):
    def __init__(self, address="192.168.1.102", port=5678):
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
                
    def readlines(self):
        while True:
            l = self.readline()
            if not l:
                self.close()
                return
            yield l
                
    def available(self):
        return bool(select.select([self.sock], [], [], 0.0)[0])

    def close(self):
        self.sock.close()
        
if __name__=="__main__":
    r = ESPRemote()
    print "Thingy on "+str(r.address)+":"+str(r.port)
    for l in r.readlines():
        print l.strip()
        