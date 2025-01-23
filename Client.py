import socket
import sys
import os
import datetime
from threading import Thread
from cryptography.fernet import *
import struct
import numpy as np
import re
from web3 import Web3
import json


class BlockchainManager:
    def __init__(self):
        # Initialize Web3 with Alchemy's Sepolia endpoint
        ALCHEMY_API_KEY = os.getenv('ALCHEMY_API_KEY')
        self.w3 = Web3(Web3.HTTPProvider(f'https://eth-sepolia.g.alchemy.com/v2/{ALCHEMY_API_KEY}'))
        
        # Load contract ABI and address
        with open('FileMetadata.json') as f:
            contract_data = json.load(f)
            self.contract = self.w3.eth.contract(
                address=contract_data['networks']['11155111']['address'],
                abi=contract_data['abi']
            )
        
        # Set up account
        self.account = self.w3.eth.account.from_key(os.getenv('ETH_PRIVATE_KEY'))
        print(f"Connected to account: {self.account.address}")

    def add_file(self, client_id, filepath, encrypted_metadata):
        """Add file metadata to blockchain"""
        file_id = self.w3.keccak(text=filepath)
        
        txn = self.contract.functions.addFile(
            client_id,
            file_id,
            encrypted_metadata
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 500000,
            'maxFeePerGas': self.w3.eth.gas_price,
            'maxPriorityFeePerGas': self.w3.eth.gas_price,
        })
        
        # Sign and send the transaction
        signed_txn = self.w3.eth.account.sign_transaction(txn, private_key=os.getenv('ETH_PRIVATE_KEY'))
        
        # Send the raw transaction using .raw property instead of .rawTransaction
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        
        # Wait for transaction receipt
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        return file_id.hex()

    def get_file_data(self, client_id, file_id):
        """Get file metadata from blockchain"""
        if isinstance(file_id, str):
            file_id = bytes.fromhex(file_id.replace('0x', ''))
            
        return self.contract.functions.getFileData(
            client_id,
            file_id
        ).call({'from': self.account.address})

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
    
def func(h,p,clientId,a,file,fname):   # Function defined for multi threading
    
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
    size=len(clientId)  
    s.sendall(size.to_bytes(4,'big'))
    s.sendall(clientId.encode())
    print("Size clientId:" , size)
    
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

            junk=s.recv(3)
            print(junk.decode())

            size=len(file[2])
            s.sendall(size.to_bytes(4,'big'))
            s.sendall(file[2])
            print("2. ",file[2])
            print("2. size:",size)
            s.close()
            return sid
        
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

def get_available_servers(registry_host='127.0.0.1', registry_port=65430):
    """Get list of available servers from registry"""
    servers = []
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((registry_host, registry_port))
            
            # Send connection type (2 for client)
            s.send(b'2')
            
            # Receive number of available servers
            size = s.recv(4)
            num_servers = int.from_bytes(size, 'big')
            
            # Receive each server's information
            for _ in range(num_servers):
                # Receive host
                size = s.recv(4)
                host_len = int.from_bytes(size, 'big')
                host = s.recv(host_len).decode()
                
                # Receive port
                port = int.from_bytes(s.recv(4), 'big')
                
                servers.append((host, port))
                
    except Exception as e:
        print(f"Error getting server list: {e}")
        
    return servers

###### Main

required_env_vars = ['ALCHEMY_API_KEY', 'ETH_PRIVATE_KEY']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
if missing_vars:
    print(f"Missing environment variables: {', '.join(missing_vars)}")
    print("Please set them before running the script.")
    exit(1)


# Before the main loop, replace hardcoded server addresses with dynamic discovery
available_servers = get_available_servers()
if not available_servers:
    print("No storage servers available")
    sys.exit(1)
else:
    print(f"Found {len(available_servers)} available servers")

clientId ='10' # input('Enter client ID.')
blockchain = BlockchainManager()
root= os.getcwd()
while (True):
    os.chdir(root)
    a= input('Press 1 to Download file.\nPress 2 to Upload file.\nPress 0 to Exit')
    exitt=0;
    
    # File uploading process 
    if (a=='2'):
        filepath=input('Enter file name')
        
        f=open(filepath,'rb')
        size=os.path.getsize(filepath)
        file = f.read(size)  # File to be uploaded is read 
        f.close()
        
        # Checking if the file already exists in the metadata
        metadataFileName = clientId + '.txt'
        if (os.path.exists(metadataFileName)):
            f = open(metadataFileName, 'r+')
            size = os.path.getsize(metadataFileName)
            print('Metadata filesize', size)
            filedata = f.read(size)
            f.close()
            
            # Create pattern that matches exact filepath after '#\n'
            pattern = r'#\n' + re.escape(filepath) + r'\n'
            if re.search(pattern, filedata):
                print("File already exists")
                continue
        
        fileKey = Fernet.generate_key()  # Encryption Key is generated 
        fernet= Fernet(fileKey)
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

        # Add shard numbers using np.insert
        newarr[0] = np.insert(newarr[0], 0, 1)
        newarr[1] = np.insert(newarr[1], 0, 2)
        newarr[2] = np.insert(newarr[2], 0, 3)

        print("Array[0]:", newarr[0])
        print("Array[1]:", newarr[1])
        print("Array[2]:", newarr[2])
        
       
        
        # Multi threading used to connect with multiple servers to Upload the file
        upload_threads = []
        for i, (server_host, server_port) in enumerate(available_servers[:3]):  # Use first 3 servers
            x = Threadvalue(target=func, args=(server_host, server_port, clientId, a, newarr[i], filepath))
            upload_threads.append(x)
            x.start()

        # Collect server IDs
        serverIds = []
        for thread in upload_threads:
            sid = thread.join()
            serverIds.append(sid)

        # Add file metadata to blockchain
        metadata = fileKey.decode() + '\n'
        k=1
        for i in range(3):
            for j in range(int(len(shards)/3)):
                wr=str(serverIds[i])+','+str(k)
                k=k+1
                metadata=metadata+wr+'\n'

        metadataKey = Fernet.generate_key()
        fernet= Fernet(metadataKey)
        encryptedMetadata = fernet.encrypt(metadata.encode())

        try:
            print("\nAdding file metadata...")
            file_id =blockchain.add_file(clientId, filepath, encryptedMetadata)
            print(f"File added with ID: {file_id}")
        
        except Exception as e:
            print(f"Error: {e}")

        # storing File id, metadata key and filename in local file
        if (not(os.path.exists(metadataFileName))):
            f=open(metadataFileName,'a+')
            f.write('#\n')
            f.write(filepath)
            f.write('\n')
            f.write(file_id)
            f.write('\n')
            f.close()
            f=open(metadataFileName,'ab')
            f.write(metadataKey)
            f.write(bytes('\n','utf-8'))
            f.close()

        else:
            f=open(metadataFileName,'r+')
            size=os.path.getsize(metadataFileName)
            print('sizee',size)
            filedata = f.read(size)
            print(len(filedata))
            pattern = r'#\n' + re.escape(filepath) + r'\n'
            if not re.search(pattern, filedata):
                print("File not found in metadata")
                f.write('#\n')
                f.write(filepath)
                f.write('\n')
                f.write(file_id)
                f.write('\n')
                f.close()
                f=open(metadataFileName,'ab')
                f.write(metadataKey)
                f.write(bytes('\n','utf-8'))
                f.close()

    # File downloading process 
    elif(a=='1'):
        namelist=[]
        flist=[]
        fileIdList=[]
        metadataKeyList=[]
        
        # Get file id, metadata key and filename from local file
        metadataFileName=clientId+'.txt'
        f=open(metadataFileName,'r')
        size=os.path.getsize(metadataFileName)
        file=f.read(size)
        f.close()
        filelist=file.split('#\n')
        filelist.remove('')
        print(filelist)
        print('Select from the following list of files.')
        for i,j in enumerate(filelist):
            temp=j.split('\n')
            print(i+1,' ',temp[0])
            fileIdList.append(temp[1])
            metadataKeyList.append(temp[2])
            namelist.append(temp[0])

        b=input('Enter serial no.')
        
        # Get metadata from blockchain
        try:
        
            print("\nRetrieving file metadata...")
            metadata = blockchain.get_file_data(clientId, fileIdList[int(b)-1])
            print(f"Retrieved metadata: {metadata}")
            
        except Exception as e:
            print(f"Error: {e}")

        # Decrypt metadata
        fernet= Fernet(metadataKeyList[int(b)-1])
        decMetadata= fernet.decrypt(metadata)
        print(decMetadata)

        # Get file key, server and shard ids from metadata
        temp=decMetadata.decode().split('\n')
        fileKey=temp[0]
        flist=temp[1:-1]
        print(fileKey)
        print(flist)

        # Multi Threading is used to connect with multiple servers in paralel to Download the file
        download_threads = []
        for server_host, server_port in available_servers:
            thread = Threadvalue(target=func, args=(server_host, server_port, clientId, a, flist, namelist[int(b)-1]))
            download_threads.append(thread)
            thread.start()

        # Collect downloaded data
        data = b''
        for thread in download_threads:
            data += thread.join()
        
        print(type(fileKey))
        print(fileKey)
        print(data)
        print(type(data))
        fernet= Fernet(fileKey)
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