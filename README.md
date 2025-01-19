# Distributed-Storage-v2

# Distributed Storage Network (Work in Progress)

A peer-to-peer distributed storage solution that allows users to share and utilize excess storage space across the network. The project implements secure file sharing with encryption, sharding, and blockchain-based metadata management.

## 🚧 Project Status: In Development

This project is currently under active development. Core file transfer and storage functionality is implemented, with blockchain integration planned for future releases.

## 🎯 Key Features

- **Distributed Storage**: Users can share their excess storage space with others in the network
- **Secure File Transfer**: Files are encrypted using Fernet symmetric encryption before transmission
- **Data Sharding**: Files are split into multiple shards for distributed storage
- **Multi-threaded Architecture**: Parallel connections for improved performance
- **Metadata Management**: Currently file-based, planned migration to blockchain

## 🔧 Technical Implementation

### Security
- Files are encrypted using the `cryptography.fernet` module before transmission
- Each file gets a unique encryption key stored in metadata
- Data is sharded and distributed across multiple storage nodes

### Network Architecture
- Client-Server model with multi-threading support
- Each storage node runs a server instance
- Clients can connect to multiple storage nodes simultaneously

### Data Management
- Files are split into 6 shards
- Shards are distributed across 3 storage nodes
- Metadata tracks file locations and encryption keys

## 🚀 Future Enhancements

- [ ] Blockchain integration for metadata storage
- [ ] Smart contract implementation for storage agreements
- [ ] Storage node reputation system
- [ ] Economic incentives for storage providers
- [ ] Enhanced security features
- [ ] Web interface for easy access

## 🛠️ Technical Requirements

- Python 3.x
- Required packages:
  - socket
  - cryptography
  - numpy
  - threading

## 💻 Usage

Currently, the system supports two main operations:

1. **Upload File**
   - File is encrypted
   - Split into shards
   - Distributed across storage nodes

2. **Download File**
   - Retrieves shards from storage nodes
   - Reassembles the file
   - Decrypts the data

## 🤝 Contributing

This is an ongoing project and contributions are welcome! Please feel free to submit pull requests or open issues for improvements.

## ⚠️ Disclaimer

This project is in development and not yet ready for production use. Use at your own risk.
