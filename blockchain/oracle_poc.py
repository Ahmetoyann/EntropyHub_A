import hashlib
import json
import os
import sys
import time
from dataclasses import asdict, dataclass

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.chaos.nihde import NIHDE
from core.pqc.dilithium3 import Dilithium3


@dataclass
class OracleResponse:
    request_id: str
    timestamp: float
    random_bytes_hex: str
    commitment_hash: str
    signature_hex: str
    oracle_public_key_hex: str


class EntropyHubOracle:
    """
    Off-chain oracle PoC:
    - Generates entropy from EntropyHub
    - Commits via SHA3-256
    - Signs commitment with Dilithium3
    """

    def __init__(self):
        self.rng = NIHDE(use_live_qrng=False)
        self.public_key, self.secret_key = Dilithium3.keygen()

    def fulfill(self, request_id: str, size: int = 32) -> OracleResponse:
        if size < 1:
            raise ValueError("size must be >= 1")

        data = bytes(self.rng.decide() for _ in range(size))
        timestamp = time.time()
        commitment = hashlib.sha3_256(request_id.encode() + timestamp.hex().encode() + data).digest()
        signature = Dilithium3.sign(self.secret_key, commitment)

        return OracleResponse(
            request_id=request_id,
            timestamp=timestamp,
            random_bytes_hex=data.hex(),
            commitment_hash=commitment.hex(),
            signature_hex=signature.hex(),
            oracle_public_key_hex=self.public_key.hex(),
        )

    @staticmethod
    def verify(response: OracleResponse) -> bool:
        commitment = bytes.fromhex(response.commitment_hash)
        signature = bytes.fromhex(response.signature_hex)
        public_key = bytes.fromhex(response.oracle_public_key_hex)
        return Dilithium3.verify(public_key, commitment, signature)


if __name__ == "__main__":
    oracle = EntropyHubOracle()
    resp = oracle.fulfill(request_id="teknofest-demo", size=32)

    print("Oracle response:")
    print(json.dumps(asdict(resp), indent=2))
    print("Signature valid:", EntropyHubOracle.verify(resp))
