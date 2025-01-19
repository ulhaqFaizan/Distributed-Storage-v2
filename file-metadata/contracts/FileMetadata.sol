// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract FileMetadata {
    struct FileData {
        bytes encryptedMetadata;  // Encrypted metadata bundle
        bool exists;
        address owner;
    }
    
    // clientID => (fileIdentifier => FileData)
    mapping(string => mapping(bytes32 => FileData)) private clientFiles;
    
    event FileAdded(string clientId, bytes32 indexed fileIdentifier);
    event FileAccessed(string clientId, bytes32 indexed fileIdentifier);

    modifier onlyOwner(string memory clientId, bytes32 fileIdentifier) {
        FileData storage fileData = clientFiles[clientId][fileIdentifier];
        require(fileData.exists, "File does not exist");
        require(fileData.owner == msg.sender, "Not the owner");
        _;
    }

    function addFile(
        string memory clientId,
        bytes32 fileIdentifier,
        bytes memory encryptedMetadata
    ) public {
        FileData storage fileData = clientFiles[clientId][fileIdentifier];
        require(!fileData.exists, "File already exists");
        
        fileData.encryptedMetadata = encryptedMetadata;
        fileData.exists = true;
        fileData.owner = msg.sender;
        
        emit FileAdded(clientId, fileIdentifier);
    }
    
    function getFileData(string memory clientId, bytes32 fileIdentifier) 
    public
    onlyOwner(clientId, fileIdentifier)
    returns (bytes memory) {
        FileData storage fileData = clientFiles[clientId][fileIdentifier];
        emit FileAccessed(clientId, fileIdentifier);
        return fileData.encryptedMetadata;
    }
} 