import hashlib
import json
import os
import sys
import time
from dataclasses import asdict, dataclass
from typing import List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.chaos.nihde import NIHDE
from core.pqc.dilithium3 import Dilithium3


@dataclass
class Block:
    index: int
    previous_hash: str
    timestamp: float
    proposer: str
    entropy_byte: int
    payload: dict
    block_hash: str
    signature: str
    proposer_public_key: str


@dataclass
class Validator:
    validator_id: str
    public_key: bytes
    secret_key: bytes


class EntropyHubDLT:
    """
    Simple PoC DLT:
    - Proposer selection seeded by EntropyHub RNG
    - Block signatures via Dilithium3
    """

    def __init__(self, validator_count: int = 4):
        if validator_count < 1:
            raise ValueError("validator_count must be >= 1")
        self.rng = NIHDE(use_live_qrng=False)
        self.validators: List[Validator] = []
        self.chain: List[Block] = []

        for i in range(validator_count):
            pk, sk = Dilithium3.keygen()
            self.validators.append(Validator(validator_id=f"validator-{i}", public_key=pk, secret_key=sk))

        self._create_genesis()

    @staticmethod
    def _hash_payload(index: int, previous_hash: str, timestamp: float, proposer: str, entropy_byte: int, payload: dict) -> bytes:
        data = {
            "index": index,
            "previous_hash": previous_hash,
            "timestamp": timestamp,
            "proposer": proposer,
            "entropy_byte": entropy_byte,
            "payload": payload,
        }
        encoded = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha3_256(encoded).digest()

    def _create_genesis(self):
        genesis_payload = {"type": "genesis", "network": "EntropyHub-DLT"}
        digest = self._hash_payload(0, "0" * 64, time.time(), "genesis", 0, genesis_payload)
        self.chain.append(
            Block(
                index=0,
                previous_hash="0" * 64,
                timestamp=time.time(),
                proposer="genesis",
                entropy_byte=0,
                payload=genesis_payload,
                block_hash=digest.hex(),
                signature="",
                proposer_public_key="",
            )
        )

    def _pick_proposer(self, entropy_byte: int) -> Validator:
        return self.validators[entropy_byte % len(self.validators)]

    def append_block(self, payload: dict) -> Block:
        entropy_byte = self.rng.decide()
        proposer = self._pick_proposer(entropy_byte)

        previous = self.chain[-1]
        index = previous.index + 1
        timestamp = time.time()
        digest = self._hash_payload(index, previous.block_hash, timestamp, proposer.validator_id, entropy_byte, payload)
        signature = Dilithium3.sign(proposer.secret_key, digest)

        block = Block(
            index=index,
            previous_hash=previous.block_hash,
            timestamp=timestamp,
            proposer=proposer.validator_id,
            entropy_byte=entropy_byte,
            payload=payload,
            block_hash=digest.hex(),
            signature=signature.hex(),
            proposer_public_key=proposer.public_key.hex(),
        )
        self.chain.append(block)
        return block

    def verify_chain(self) -> bool:
        for i in range(1, len(self.chain)):
            prev = self.chain[i - 1]
            current = self.chain[i]
            if current.previous_hash != prev.block_hash:
                return False

            digest = self._hash_payload(
                current.index,
                current.previous_hash,
                current.timestamp,
                current.proposer,
                current.entropy_byte,
                current.payload,
            )
            if digest.hex() != current.block_hash:
                return False

            if not Dilithium3.verify(
                bytes.fromhex(current.proposer_public_key),
                digest,
                bytes.fromhex(current.signature),
            ):
                return False
        return True

    def export_chain(self):
        return [asdict(block) for block in self.chain]


if __name__ == "__main__":
    ledger = EntropyHubDLT(validator_count=4)
    ledger.append_block({"type": "tx", "from": "alice", "to": "bob", "amount": 12})
    ledger.append_block({"type": "tx", "from": "bob", "to": "carol", "amount": 7})

    print(f"Chain length: {len(ledger.chain)}")
    print(f"Chain valid: {ledger.verify_chain()}")
