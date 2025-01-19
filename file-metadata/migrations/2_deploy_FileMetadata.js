const FileMetadata = artifacts.require("FileMetadata");

module.exports = function(deployer) {
  deployer.deploy(FileMetadata);
}; 