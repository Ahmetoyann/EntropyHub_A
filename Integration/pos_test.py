import random
import hashlib
from web3 import Web3
from solcx import compile_standard, install_solc

# --- PoS Simulation Classes ---
class Validator:
    def __init__(self, address, stake):
        self.address = address
        self.stake = stake
        self.blocks_produced = 0

class PoSSimulation:
    def __init__(self, validators):
        self.validators = validators

    def get_classic_random_validator(self):
        # Classic weighted random selection
        weights = [v.stake for v in self.validators]
        return random.choices(self.validators, weights=weights, k=1)[0]

    def get_entropy_hub_validator(self, entropy_seed):
        # Mixing the seed from EntropyHub with SHA-256 for selection
        # entropy_seed: Byte array from EntropyHub service
        combined_hash = hashlib.sha256(entropy_seed).hexdigest()
        
        # Convert hash to a number and take modulo by total stake
        total_stake = sum(v.stake for v in self.validators)
        selector = int(combined_hash, 16) % total_stake
        
        current_sum = 0
        for v in self.validators:
            current_sum += v.stake
            if selector < current_sum:
                return v

ganache_url = "http://127.0.0.1:8545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

if web3.is_connected():
    print("Connected to Local Blockchain (Ganache)!")
    # Check the first account and its balance
    account_0 = web3.eth.accounts[0]
    balance = web3.eth.get_balance(account_0)
    print(f"Account: {account_0}")
    print(f"Balance: {web3.from_wei(balance, 'ether')} ETH")

    # --- Smart Contract Deployment (PoS Validator Selector) ---
    try:
        # 1. Read Solidity Code
        with open("PoSValidatorSelector.sol", "r") as file:
            pos_contract_source = file.read()

        # 2. Compile
        print("Compiling Solidity code (v0.8.0)...")
        install_solc("0.8.0") # Downloads compiler on first run
        compiled_sol = compile_standard(
            {
                "language": "Solidity", 
                "sources": {"PoSValidatorSelector.sol": {"content": pos_contract_source}},
                "settings": {"outputSelection": {"*": {"*": ["abi", "evm.bytecode"]}}},
            },
            solc_version="0.8.0",
        )
        bytecode = compiled_sol["contracts"]["PoSValidatorSelector.sol"]["PoSValidatorSelector"]["evm"]["bytecode"]["object"]
        abi = compiled_sol["contracts"]["PoSValidatorSelector.sol"]["PoSValidatorSelector"]["abi"]

        # 3. Deploy
        PoSContract = web3.eth.contract(abi=abi, bytecode=bytecode)
        tx_hash = PoSContract.constructor().transact({"from": account_0})
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Create contract instance
        pos_contract_instance = web3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
        print(f"PoS Selector Contract Deployed! Address: {tx_receipt.contractAddress}")

        # 4. Add Validators to Blockchain (Use Ganache Accounts)
        # Node_A -> accounts[1], Node_B -> accounts[2], Node_C -> accounts[3]
        if len(web3.eth.accounts) >= 4:
            val_stakes = [500, 300, 200]
            print("Registering validators to smart contract...")
            for i, stake in enumerate(val_stakes, 1):
                addr = web3.eth.accounts[i]
                pos_contract_instance.functions.addValidator(addr, stake).transact({"from": account_0})
                print(f"  -> Validator Added: {addr} (Stake: {stake})")

    except Exception as e:
        print(f"Contract deployment error: {e}")
else:
    print("Connection failed. Is Ganache running?")

# --- Run PoS Simulation ---
print("\n--- PoS Validator Selection Simulation ---")
# Create validator set (Address, Stake amount)
validators = [
    Validator("Node_A", 500),
    Validator("Node_B", 300),
    Validator("Node_C", 200)
]
sim = PoSSimulation(validators)

# --- 1. Classic Method ---
for _ in range(1000):
    winner = sim.get_classic_random_validator()
    winner.blocks_produced += 1

print("Classic Random Results:")
for v in validators:
    print(f"{v.address}: {v.blocks_produced} blocks")
    v.blocks_produced = 0 # Reset

print("-" * 30)

# --- 2. EntropyHub Integrated Method ---
for i in range(1000):
    # Simulated EntropyHub output (Chaos + SHA-256 mixed byte)
    mock_entropy_hub_output = f"kaos_verisi_{i}_{random.random()}".encode() 
    
    winner = sim.get_entropy_hub_validator(mock_entropy_hub_output)
    winner.blocks_produced += 1
    
    # Example: Verify on Blockchain in the first iteration
    if i == 0 and 'pos_contract_instance' in locals():
        print("\n--- Live Selection Test on Blockchain ---")
        on_chain_winner = pos_contract_instance.functions.selectValidator(mock_entropy_hub_output).call()
        print(f"Entropy Seed: {mock_entropy_hub_output}")
        print(f"Address Selected by Smart Contract: {on_chain_winner}")
        print("-" * 30)

print("EntropyHub Integrated Results:")
for v in validators:
    print(f"{v.address}: {v.blocks_produced} blocks")