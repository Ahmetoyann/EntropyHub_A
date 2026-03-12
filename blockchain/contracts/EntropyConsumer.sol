// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IEntropyHubOracle {
    function results(bytes32 requestId)
        external
        view
        returns (
            bytes memory randomBytes,
            bytes32 commitmentHash,
            uint256 timestamp,
            bytes memory signature,
            bytes memory oraclePublicKey
        );
}

contract EntropyConsumer {
    IEntropyHubOracle public oracle;
    bytes public latestRandom;

    constructor(address oracleAddress) {
        oracle = IEntropyHubOracle(oracleAddress);
    }

    function consume(bytes32 requestId) external {
        (bytes memory randomBytes,,,,) = oracle.results(requestId);
        require(randomBytes.length > 0, "empty entropy");
        latestRandom = randomBytes;
    }
}
