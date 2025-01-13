import socket
import sys
import os
import datetime
from threading import Thread
from cryptography.fernet import *
import struct
import numpy as np

# This class is created to return value from the thread
class Threadvalue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        print(type(self._target))
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return
    
def func(h,p,cid,a,file,fname):   # Function defined for multi threading
    
    HOST = h  # The server's IP address
    PORT = p        # The port used by the server
    
    compdata = bytearray()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Socket type object is created 
    s.connect((HOST, PORT)) # Connection with the server is bulid
    print('connected to server')
    '''
    size=s.recv(4)
    s1=int.from_bytes(size,'big')
    buff=s.recv(s1)
    print('Server: '+buff.decode())
    '''
    
    # Initial data is being transfered 
    size=len(cid)  
    s.sendall(size.to_bytes(4,'big'))
    s.sendall(cid.encode())
    print("Size cid:" , size)
    
    size=s.recv(4)
    s1=int.from_bytes(size,'big')
    sid = s.recv(s1)
    sid = sid.decode()
    print("Serverid: ",sid)
    print("Serverid size: ",s1)
    
    size=len(fname)
    s.sendall(size.to_bytes(4,'big'))
    s.sendall(fname.encode())
    filelist={}
    while True:
        size=len(a)
        s.sendall(size.to_bytes(4,'big'))
        s.sendall(a.encode())
        
        # uploading process 
        if (a=='2'):   
            size=len(file[0])
            s.sendall(size.to_bytes(4,'big'))
            s.sendall(file[0])
            print("1. ", file[0])
            print("1 size:" , size)
            
            junk=s.recv(3)
            print(junk.decode())
            
            size=len(file[1])
            s.sendall(size.to_bytes(4,'big'))
            s.sendall(file[1])
            print("2. ",file[1])
            print("2. size:",size)
            break
        
        # Downloading process 
        elif (a == '1'):
            shardid=[]
            data=b''
            print(file)
            for i in range(len(file)):
                serverid= file[i]
                if(serverid[0]==sid):
                    shardid.append(serverid[2])
            size=len(shardid)
            s.sendall(size.to_bytes(4,'big'))
            for i in range(len(shardid)):
                size=len(shardid[i])
                s.sendall(size.to_bytes(4,'big'))
                s.sendall(shardid[i].encode())
                #print(shardid[i])
                size=s.recv(4)
                s1=int.from_bytes(size,'big')
                buff=b''
                while len(buff) < s1 :
                    buff += s.recv(s1)
                data=data+buff
            #print(data)
            s.close()
            return data
        
        else:
            continue

###### Main
h='192.168.0.2'
h1='192.168.0.3'
h2='192.168.0.5'
p=65432
p1=65434
p2=65435

cid ='12' # input('Enter client ID.')
root= os.getcwd()
while (True):
    os.chdir(root)
    a= input('Press 1 to Download file.\nPress 2 to Upload file.\nPress 0 to Exit')
    exitt=0;
    
    # File uploading process 
    if (a=='2'):
        filepath=input('Enter file name')
        key = Fernet.generate_key()  # Encryption Key is generated 
        fernet= Fernet(key)
        f=open(filepath,'rb')
        size=os.path.getsize(filepath)
        file = f.read(size)  # File to be uploaded is read 
        f.close()
        
        encfile= fernet.encrypt(file)  # File is encrypted 
        
        fsize=len(encfile)
        print("Encrypted File:", encfile)
        print("size of Encrypted file:",fsize)
        
        # Sharding process 
        if(fsize%6==0):
            chunksize= fsize//6
        else:
            chunksize= fsize//6+1
        
        print("Chunksize:" , chunksize)
        shards = [encfile[i:i+chunksize] for i in range(0,fsize,chunksize)]
        print("shards", shards)
        
        arr = np.array(shards)
        newarr = np.array_split(arr, 3)
        print("Array[0]:" ,newarr[0])
        print("Array[1]:" ,newarr[1])
        print("Array[2]:" ,newarr[2])
        
        # Metadata is created 
        filename=cid+'.txt'
        if (not(os.path.exists(filename))):
            f=open(filename,'a+')
            f.write('#\n')
            f.write(filepath)
            f.write('\n')
            f.close()
            f=open(filename,'ab')
            f.write(key)
            f.write(bytes('\n','utf-8'))
            f.close()
            f=open(filename,'a+')
            k=1;
            for i in range(3):
                for j in range(int(len(shards)/3)):
                    wr=str(i)+','+str(k)
                    k=k+1
                    f.write(wr)
                    f.write('\n')
            f.close()
        else:
            f=open(filename,'r+')
            size=os.path.getsize(filename)
            print('size',size)
            filedata = f.read(size)
            print(len(filedata))
            if (filedata.find(filepath) == -1):
                f.write('#\n')
                f.write(filepath)
                f.write('\n')
                f.close()
                f=open(filename,'ab')
                f.write(key)
                f.write(bytes('\n','utf-8'))
                f.close()
                f=open(filename,'a+')
                k=1;
                for i in range(3):
                    for j in range(int(len(shards)/3)):
                        wr=str(i)+','+str(k)
                        k=k+1
                        f.write(wr)
                        f.write('\n')
                f.close()
            else:
                print('File already exists')
                exitt=1
        if(exitt==1):
            continue
        
        # Multi threading used to connect with multiple servers 
        x=Threadvalue(target=func, args =(h,p,cid,a,newarr[0],filepath))  
        y=Threadvalue(target=func, args=(h1,p1,cid,a,newarr[1],filepath))
        z=Threadvalue(target=func, args=(h2,p2,cid,a,newarr[2],filepath))
        x.start()
        x.join()
        y.start()
        y.join()
        z.start()
        z.join()
    
    # File downloading process 
    elif(a=='1'):
        namelist=[]
        flist=[]
        
        # Metadata is accessed 
        filename=cid+'.txt'
        f=open(filename,'r')
        size=os.path.getsize(filename)
        file=f.read(size)
        f.close()
        #print(type(file))
        filelist=file.split('#\n')
        filelist.remove('')
        print(filelist)
        print('Select from the following list of files.')
        for i,j in enumerate(filelist):
            temp=j.split('\n')
            #if(i!=0):
            print(i+1,' ',temp[0])
            namelist.append(temp[0])
            flist.append(temp)
            flist[i].remove(temp[0])
            flist[i].remove('')
            flist[i].remove(temp[0])
        
        print(flist)
        
        b=input('Enter serial no.')
        
        # Multi Threading is used to connect with multiple servers in paralel 
        x=Threadvalue(target=func, args =(h,p,cid,a,flist[int(b)-1],namelist[int(b)-1]))
        y=Threadvalue(target=func, args=(h1,p1,cid,a,flist[int(b)-1],namelist[int(b)-1]))
        z=Threadvalue(target=func, args=(h2,p2,cid,a,flist[int(b)-1],namelist[int(b)-1]))
        x.start()
        data1=x.join()
        y.start()
        data2=y.join()
        z.start()
        data3=z.join()
        '''
        temp1=''.join([str(i) for i in data1])
        temp2=''.join([str(i) for i in data2])
        temp3=''.join([str(i) for i in data3])
        '''
        # Data shards are joined together 
        data= data1+data2+data3
        
        f=open(filename,'rb')
        size=os.path.getsize(filename)
        file=f.readlines(size)
        f.close()
        j=0
        for i,k in enumerate(file):
            print(k.decode())
            if(k.decode()=='#\r\n'):
                j=j+1
                print('j=',j)
                if(j==int(b)):
                    keyy=file[i+2]  # Key is read from the metadata for decryption 
                    print('b')
        #ke=bytes(keyy,'base64')
        key=keyy[:-1]
        print(type(key))
        print(key)
        #filelist=file.split('#\n')
        print(data)
        print(type(data))
        fernet= Fernet(key)
        decfile= fernet.decrypt(data)  # Decryption of file 
        print(decfile)
        
        # Decrypted file stored into the PC 
        folder=datetime.datetime.now().date()
        curfol= os.getcwd()
        a,c=os.path.split(curfol)
        if (not(os.path.exists(str(folder))) and c!=str(folder)):
                os.mkdir(str(folder))
        
        if(c!=str(folder)):
            os.chdir(str(folder))
        print(namelist[int(b)-1])
        
        f=open(namelist[int(b)-1],'wb')
        f.write(decfile)
        f.close()
    elif (a=='0'):
        break