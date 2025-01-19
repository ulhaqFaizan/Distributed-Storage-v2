from web3 import Web3
import json
import os
from cryptography.fernet import Fernet

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

    def add_file(self, clientId, filepath, encrypted_metadata):
        """Add file metadata to blockchain"""
        file_id = self.w3.keccak(text=filepath)
        
        txn = self.contract.functions.addFile(
            clientId,
            file_id,
            encrypted_metadata
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 200000,
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

    def get_file_data(self, clientId, file_id):
        """Get file metadata from blockchain"""
        if isinstance(file_id, str):
            file_id = bytes.fromhex(file_id.replace('0x', ''))
            
        return self.contract.functions.getFileData(
            clientId,
            file_id
        ).call({'from': self.account.address})

def test_contract_interaction():
    blockchain = BlockchainManager()
    
    # Test data
    clientId = "test_client"
    test_file = "example.txt"
    test_metadata = b"encrypted_metadata_example"
    
    try:
        print("\nAdding file metadata...")
        file_id = blockchain.add_file(clientId, test_file, test_metadata)
        print(f"File added with ID: {file_id}")
        
        print("\nRetrieving file metadata...")
        metadata = blockchain.get_file_data(clientId, file_id)
        print(f"Retrieved metadata: {metadata}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    required_env_vars = ['ALCHEMY_API_KEY', 'ETH_PRIVATE_KEY']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Missing environment variables: {', '.join(missing_vars)}")
        print("Please set them before running the script.")
        exit(1)
    
    success = test_contract_interaction()
    if success:
        print("\nContract interaction test completed successfully!")
    else:
        print("\nContract interaction test failed!")