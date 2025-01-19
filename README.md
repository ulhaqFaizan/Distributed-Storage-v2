# Distributed-Storage-v2

# Distributed Storage Network (Work in Progress)

A peer-to-peer distributed storage solution that allows users to share and utilize excess storage space across the network. The project implements secure file sharing with encryption, sharding, and blockchain-based metadata management on Ethereum's Sepolia testnet.

## 🚧 Project Status: In Development

Core functionality is implemented including:
- File transfer and storage
- Blockchain integration for metadata management
- Multi-threaded architecture
- Encryption and sharding

## 🎯 Key Features

- **Distributed Storage**: Users can share their excess storage space with others in the network
- **Secure File Transfer**: Files are encrypted using AES encryption before transmission
- **Data Sharding**: Files are split into 6 shards and distributed across 3 storage nodes
- **Multi-threaded Architecture**: Parallel connections for improved performance
- **Blockchain Metadata**: File metadata stored securely on Ethereum Sepolia testnet
- **Smart Contract Integration**: Secure metadata management with ownership verification

## 🔧 Technical Implementation

### Security
- Files are encrypted using the `cryptography.fernet` module before transmission
- Each file gets a unique encryption key
- Metadata is encrypted before being stored on the blockchain
- Smart contract enforces ownership verification for file access
- Data is sharded and distributed across multiple storage nodes

### Network Architecture
- Client-Server model with multi-threading support
- Each storage node runs a server instance
- Clients can connect to multiple storage nodes simultaneously
- Currently designed for exactly 3 storage nodes (will be generalized in future updates)
- Parallel shard transfer using multiple connections
- Blockchain integration for metadata management

### Data Management
- Files are split into 6 shards
- Shards are distributed evenly across 3 storage nodes
- Metadata stored on Ethereum blockchain includes:
  - File encryption key
  - Shard locations
  - Server mappings
  - Ownership information

## 🚀 Future Enhancements

- [ ] Support for dynamic number of storage providers
- [ ] Economic incentives for storage providers
- [ ] Enhanced security features
- [ ] Web interface for easy access

## 🛠️ Technical Requirements

- Python 3.8+
- Ethereum wallet with Sepolia testnet ETH
- Required packages:
  - web3
  - socket
  - cryptography
  - numpy
  - threading

## 💻 Environment Setup

1. Create a `.env` file with:
ALCHEMY_API_KEY=your_alchemy_api_key
ETH_PRIVATE_KEY=your_ethereum_private_key

2. Install dependencies

## 🚀 Usage

1. **Start Storage Servers**
   - Run each server on different ports (65432, 65434, 65435)
   - Servers automatically create storage directories

2. **Upload File**
   - File is encrypted
   - Split into 6 shards
   - Distributed across 3 storage nodes
   - Metadata stored on blockchain

3. **Download File**
   - Retrieves metadata from blockchain
   - Fetches shards from storage nodes
   - Reassembles and decrypts the file

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for improvements.

## ⚠️ Disclaimer

This project is in development. While core functionality is implemented and tested, use in production environments is not recommended without additional security auditing.