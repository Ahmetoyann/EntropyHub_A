// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract EntropyHubOracle {
    struct OracleResult {
        bytes randomBytes;
        bytes32 commitmentHash;
        uint256 timestamp;
        bytes signature;
        bytes oraclePublicKey;
    }

    address public owner;
    mapping(bytes32 => OracleResult) public results;

    event OracleFulfilled(
        bytes32 indexed requestId,
        bytes randomBytes,
        bytes32 commitmentHash,
        uint256 timestamp
    );

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "not owner");
        _;
    }

    function submitEntropy(
        bytes32 requestId,
        bytes calldata randomBytes,
        bytes32 commitmentHash,
        uint256 timestamp,
        bytes calldata signature,
        bytes calldata oraclePublicKey
    ) external onlyOwner {
        results[requestId] = OracleResult({
            randomBytes: randomBytes,
            commitmentHash: commitmentHash,
            timestamp: timestamp,
            signature: signature,
            oraclePublicKey: oraclePublicKey
        });

        emit OracleFulfilled(requestId, randomBytes, commitmentHash, timestamp);
    }
}
