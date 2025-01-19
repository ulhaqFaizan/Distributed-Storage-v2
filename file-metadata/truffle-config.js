require('dotenv').config();
const HDWalletProvider = require('@truffle/hdwallet-provider');

const { PRIVATE_KEY, ALCHEMY_API_KEY } = process.env;

module.exports = {
  // Specify the Solidity compiler version
  compilers: {
    solc: {
      version: "0.8.0",    // Fetch exact version from solc-bin (default: truffle's version)
    }
  },
  
  networks: {
    // Development network (Ganache)
    development: {
      host: "127.0.0.1",     // Localhost
      port: 8545,            // Standard Ganache port
      network_id: "*"        // Any network
    },
    
    // Sepolia Testnet
    sepolia: {
      provider: () => new HDWalletProvider(
        PRIVATE_KEY, // Wallet private key
        `https://eth-sepolia.g.alchemy.com/v2/${ALCHEMY_API_KEY}`
      ),
      network_id: 11155111,       // Sepolia's network id
      gas: 5500000,               // Gas limit, adjust as needed
      confirmations: 2,           // # of confirmations to wait between deployments
      timeoutBlocks: 200,         // # of blocks before a deployment times out
      skipDryRun: true            // Skip dry run before migrations? (default: false for public nets)
    }
  }
}; 