#!/usr/bin/env python
#encoding: utf-8

import socket
import os
import random
import re

PKTFIXEDLEN = 512
N = 15
UDP_IP = '0.0.0.0'
UDP_PORT = 8889

# 获得ACK或SEQ序号
def header(data):
    retval = -1
    if data[0]=='A':
        retval = int(re.match(r'ACK:([\-0-9]+)\r\n\r\n',data).group(1))
    elif data[0]=='S':
        retval = int(re.match(r'SEQ:([\-0-9]+)\r\n\r\n',data).group(1))
    return retval

class linknode():
    def __init__(self,seq):
        self.seq = seq
        self.chk = False
        self.next = None
        self.data = None

class ThreadVar():
    def __init__(self):
        self.tail = None
        self.base = None
        self.revbuf = None

def init_windows(theadvar):
    curptr = theadvar.base
    for i in range(0,15):
        if i == 0:
            continue
        else:
            curptr.next = linknode(theadvar.tail.seq+PKTFIXEDLEN)
            curptr = curptr.next
            theadvar.tail = curptr

threadvar = ThreadVar()
threadvar.base = linknode(0)
threadvar.tail = threadvar.base
threadvar.revbuf = ''
init_windows(threadvar)
recvfinish = False

def scanwindows(seq,data,sock,theadvar,addr):
    if seq <= theadvar.tail.seq and seq != -2:
        print "recv data:"+repr(data)
        sock.sendto("ACK:" + str(seq)+'\r\n\r\n', addr)
    if seq < theadvar.base.seq:
        return False
    elif seq == theadvar.base.seq:
        theadvar.base.chk = True  
        theadvar.base.data = data
        while theadvar.base.chk:
            prefix = re.match(r'SEQ:[0-9]+\r\n\r\n',theadvar.base.data).group(0)
            theadvar.base.data = theadvar.base.data[len(prefix):]
            theadvar.revbuf += theadvar.base.data
            theadvar.base = theadvar.base.next
            theadvar.tail.next = linknode(theadvar.tail.seq + PKTFIXEDLEN)
            theadvar.tail = theadvar.tail.next 
            print 'slide a window!' 
            print 'base:'+str(theadvar.base.seq)
            print 'tail:'+str(theadvar.tail.seq)
    elif seq <= theadvar.tail.seq and seq > theadvar.base.seq:
        curptr = theadvar.base
        while curptr.seq < seq:
            curptr = curptr.next
        if curptr.seq == seq:
            curptr.chk = True
            curptr.data = data

def recvdata(data,addr): 
    print "func : recvdata"
    global recvfinish   
    if recvfinish:
        return 
    seq =  header(data)
    if seq == -2:
        sock.sendto("ACK:"+str(-2)+'\r\n\r\n',addr)
        recvfinish = True
    scanwindows(seq,data,sock,threadvar,addr)

def sendterminalsg(sock, val=-2):
    expseq = val
    if random.randint(0, 5) != 0:
        sock.sendto("SEQ:" + str(expseq) + "\r\n\r\n", dest)
    acknowledged = False
    ctnto = 0
    while not acknowledged:
        try:
            ACK, address = sock.recvfrom(1024)
            ctnto = 0
            # print ACK
            ackseq = header(ACK)
            # print ackseq
            # print expseq
            if ACK[0]=='S':
                recvdata(ACK,address)
                continue
            elif ackseq == expseq:
                acknowledged = True
        except socket.timeout:
            ctnto += 1
            if random.randint(0, 5) != 0:
                sock.sendto("SEQ:" + str(expseq) + "\r\n\r\n", dest)
            if ctnto == 10:
                break


class linknode():

    def __init__(self,seq):
        self.seq = seq
        self.chk = False
        self.next = None

def init_windows():
    global base
    global user_input
    global expseq
    global sock
    global tail
    global expseq_tl
    global raw_str
    global dest
    curptr = base
    for i in range(0, 15):
            if not user_input:
                break
            user_input = 'SEQ:' + str(expseq) + '\r\n\r\n' + user_input
            if random.randint(0, 5) != 0:
                sock.sendto(user_input, dest)
            if i == 0:
                continue
            else:
                curptr.next=linknode(expseq)                
                curptr=curptr.next
                tail = curptr
            expseq = expseq_tl
            expseq_tl = min(expseq + PKTFIXEDLEN, len(raw_str))
            user_input = raw_str[expseq:expseq_tl]

def slide():
    global user_input
    global expseq
    global sock
    global expseq_tl
    global raw_str
    global dest
    if not user_input:
        return linknode(-2)
    user_input = 'SEQ:' + str(expseq) + '\r\n\r\n' + user_input
    if random.randint(0, 5) != 0:
        sock.sendto(user_input, dest)
    retnode = linknode(expseq)
    expseq = expseq_tl    
    expseq_tl = min(expseq + PKTFIXEDLEN, len(raw_str))
    user_input = raw_str[expseq:expseq_tl]
    return retnode

def resend():
    global base
    global raw_str
    global sock
    global dest
    curptr = base
    while curptr and curptr!=-2:
        tmpend=min(curptr.seq+PKTFIXEDLEN,len(raw_str))        
        if random.randint(0, 5) != 0 and not curptr.chk and curptr.seq != -2:
            print 'resend seq:' + str(curptr.seq) 
            print dest
            sock.sendto('SEQ:' + str(curptr.seq) + '\r\n\r\n' +raw_str[curptr.seq:tmpend], dest)
        curptr = curptr.next

if __name__ == '__main__':
    
    base = linknode(0)
    tail = base

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    sock.settimeout(0.5)
    print 'DST IP:',
    destaddr = raw_input()
    dest = (destaddr, 8888)
    raw_str = ''
    expseq = 0
    print "filename:",
    filename = raw_input()
    with open(filename, 'rb') as f:
        raw_str = f.read()
    expseq_tl = min(expseq + PKTFIXEDLEN, len(raw_str))
    # print raw_str
    user_input = raw_str[expseq:expseq_tl]


    #print expseq
    # print expseq_tl
    init_windows()
    #acknowledged = False
    #seqchgfg = False
    sendfinish =False
    while True:
        try:
            print 1
            if base.seq == -2:
                print 8
                if sendfinish == False:
                    print 9
                    sendterminalsg(sock)
                    print 10
                    #sendterminalsg(sock, -3)
                    sendfinish = True
                    print "OK!!!!!!"
            if base.seq==-2 and recvfinish:
                print 4
                break
            ACK, address = sock.recvfrom(1024)
            if ACK[0]=='S' or base.seq==-2:
                print 6
                recvdata(ACK,address)
                print 5
                continue
            print repr(ACK)
            ackseq = header(ACK)
            print 7
            # print ackseq
            print 'nextseq:'+str(expseq)    
            curptr = base    
            while curptr.seq < ackseq and curptr.seq != -2:
                #print 'base:'+str(base.seq)
                curptr=curptr.next 
            if base.seq == ackseq: 
                base.chk = True
                while base.chk :      
                    print 3   
                    base = base.next
                    tail.next= slide()
                    if tail.next.seq == -2:
                        print 'new base:'+str(base.seq)
                        print 'EOF!'
                    else:
                        tail = tail.next
                        print 'new base:'+str(base.seq)
                        print 'slide a window!'  
            elif curptr.seq == ackseq:
                curptr.chk = True     
        except socket.timeout:
            print 'timeout!'
            resend()
    print repr(ACK)
    # if not seqchgfg:
    #    expseq = expseq_tl


    sock.close()
    outfile = raw_input('output filename:')
    with open(outfile, 'wb') as f:
        f.write(threadvar.revbuf)
