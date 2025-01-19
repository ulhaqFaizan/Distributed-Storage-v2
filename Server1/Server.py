import socket
import time
import sys
import os
import threading

def func(x,y):
    conn=x
    addr=y
    sid='1'
    
    with conn:
        print('Connected by', addr)
        '''
        size=sys.getsizeof('Welcome to File Server')
        conn.sendall(size.to_bytes(4,'big'))
        conn.sendall(b'Welcome to File Server')
        '''
        size=conn.recv(4)
        s1=int.from_bytes(size,'big')
        clientid = conn.recv(s1)
        clientid = clientid.decode()
        print("clientid: ",clientid)
        print("clientid size: ",s1)
        
        size=len(sid)
        conn.sendall(size.to_bytes(4,'big'))
        conn.sendall(sid.encode())
        print("Size sid:" , size)
        buff=conn.recv(4)
        s1=int.from_bytes(buff,'big')
        fname=conn.recv(s1)
        
        size=conn.recv(4)
        s1=int.from_bytes(size,'big')
        buff=conn.recv(s1)
        print('a:'+buff.decode())
        
        if (buff.decode()=='2'):
            size=conn.recv(4)
            s1=int.from_bytes(size,'big')
            print('s',s1)
            buff = conn.recv(s1)
            print(buff)
            
            conn.sendall('abc'.encode())
            
            size=conn.recv(4)
            s1=int.from_bytes(size,'big')
            print('s',s1)
            buff1=b''
            while len(buff1) < s1:
                 buff1 += conn.recv(s1)
            print(buff1)

            conn.sendall('abc'.encode())
            
            size=conn.recv(4)
            s1=int.from_bytes(size,'big')
            print('s',s1)
            buff2=b''
            while len(buff2) < s1:
                 buff2 += conn.recv(s1)
            print(buff2)
            
            curfol= os.getcwd()
            if (not(os.path.exists(clientid)) and curfol!=clientid):
                os.mkdir(clientid)
            if(curfol!=clientid):
                os.chdir(clientid)
            
            curfol= os.getcwd()
            if (not(os.path.exists(fname)) and curfol!=fname):
                os.mkdir(fname)
            if(curfol!=fname):
                os.chdir(fname)
                
            
            filname=str(int(buff)*2 - 1)+ '.txt'
            print(type(filname))
            f=open(filname,'wb')
            f.write(buff1)
            f.close()
            filname=str(int(buff)*2)+ '.txt'
            print(type(filname))
            f=open(filname,'wb')
            f.write(buff2)
            f.close()
            
            '''
            filelist = os.listdir("C:\FileServer\\")
            size = len(filelist)
            conn.sendall(size.to_bytes(4,'big'))
            for i in filelist:
                size = sys.getsizeof(i)
                conn.sendall(size.to_bytes(4,'big'))
                conn.sendall(i.encode())
                tosend=os.path.getsize("C:\FileServer\\"+i)
                conn.sendall(tosend.to_bytes(4,'big'))
            
            size=sys.getsizeof('Choose the file from the list above.\n\tEnter the serial number of the file you want to download.')
            conn.sendall(size.to_bytes(4,'big'))
            conn.sendall(b'Choose the file from the list above.\n\tEnter the serial number of the file you want to download.')
            '''    
        elif (buff.decode()=='1'):
            curfol= os.getcwd()
            if(curfol!=clientid):
                os.chdir(clientid)
            
            curfol= os.getcwd()
            if(curfol!=fname):
                os.chdir(fname)
                
            size=conn.recv(4)
            sh=int.from_bytes(size,'big')
            for i in range(sh):
                buff=conn.recv(4)
                s1=int.from_bytes(buff,'big')
                buff=conn.recv(s1)
                print('b',buff.decode())
                filename=buff.decode()+'.txt'
                f=open(filename,'rb')
                fsend=f.read()
                f.close()
                size = len(fsend)
                conn.sendall(size.to_bytes(4,'big'))
                conn.sendall(fsend)
                #conn.close()
                #break
            '''
            curfol= os.getcwd()
            a,b=os.path.split(curfol)
            if (not(os.path.exists(str(clientid))) and b!=str(clientid)):
                    os.mkdir(str(clientid))
            
            if(b!=str(folder)):
                os.chdir(str(clientid))
    
            '''
            
        elif(buff.decode()=='0'):
            conn.close()
        '''
        else:
            continue
        size=conn.recv(4)
        s1=int.from_bytes(size,'big')
        buff=conn.recv(s1)
        print('client:'+buff.decode())
        if buff.decode() == 'bye':
            conn.close()
            break
        
        filename=buff.decode()
        f=open("C:\FileServer\\"+filename,'rb')
        size=os.path.getsize("C:\FileServer\\"+filename)
        tosend=f.read(size)
        f.close()
        conn.sendall(size.to_bytes(4,'big'))
        conn.sendall(tosend)
        '''
        conn.close()  
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)
curdir=os.getcwd()

buff = b''
buff1=b''
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(5)
    while True:
        os.chdir(curdir)
        print('ready to accept')
        conn, addr = s.accept()
        x=threading.Thread(target=func, args=(conn,addr))
        x.start()