// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract PoSValidatorSelector {
    struct Validator {
        address addr;
        uint256 stake;
    }

    Validator[] public validators;
    uint256 public totalStake;

    function addValidator(address _addr, uint256 _stake) public {
        validators.push(Validator(_addr, _stake));
        totalStake += _stake;
    }

    function selectValidator(bytes memory entropySeed) public view returns (address) {
        require(totalStake > 0, "No validators");
        
        // EntropyHub'dan gelen seed'i keccak256 ile hashle (Python'daki sha256'ya denk)
        uint256 randomValue = uint256(keccak256(entropySeed));
        
        // Toplam stake üzerinden mod al
        uint256 selector = randomValue % totalStake;
        
        uint256 currentSum = 0;
        for (uint256 i = 0; i < validators.length; i++) {
            currentSum += validators[i].stake;
            if (selector < currentSum) {
                return validators[i].addr;
            }
        }
        return validators[validators.length - 1].addr;
    }
}