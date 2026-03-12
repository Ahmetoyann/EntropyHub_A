import hashlib
from pqcrypto.sign import ml_dsa_65
import importlib


class Dilithium3:
    """Real Dilithium/ML-DSA signature wrapper via pqcrypto (primary) and liboqs (fallback)."""

    MECHANISMS = ("Dilithium3", "ML-DSA-65")

    @classmethod
    def _select_mechanism(cls) -> str:
        try:
            oqs = importlib.import_module("oqs")
        except BaseException:
            oqs = None
        if oqs is None:
            return ""
        available = set(oqs.get_enabled_sig_mechanisms())
        for name in cls.MECHANISMS:
            if name in available:
                return name
        return ""

    @classmethod
    def keygen(cls):
        try:
            return ml_dsa_65.generate_keypair()
        except Exception:
            mechanism = cls._select_mechanism()
            if not mechanism:
                raise RuntimeError("No real Dilithium backend available (pqcrypto/liboqs).")
            oqs = importlib.import_module("oqs")
            with oqs.Signature(mechanism) as signer:
                public_key = signer.generate_keypair()
                secret_key = signer.export_secret_key()
            return public_key, secret_key

    @classmethod
    def sign(cls, secret_key: bytes, message: bytes) -> bytes:
        if not isinstance(message, (bytes, bytearray)):
            raise TypeError("message must be bytes")
        try:
            return ml_dsa_65.sign(bytes(secret_key), bytes(message))
        except Exception:
            mechanism = cls._select_mechanism()
            if not mechanism:
                raise RuntimeError("No real Dilithium backend available (pqcrypto/liboqs).")
            oqs = importlib.import_module("oqs")
            with oqs.Signature(mechanism, secret_key=bytes(secret_key)) as signer:
                return signer.sign(bytes(message))

    @classmethod
    def verify(cls, public_key: bytes, message: bytes, signature: bytes) -> bool:
        if not isinstance(message, (bytes, bytearray)):
            raise TypeError("message must be bytes")
        try:
            return bool(ml_dsa_65.verify(bytes(public_key), bytes(message), bytes(signature)))
        except Exception:
            mechanism = cls._select_mechanism()
            if not mechanism:
                return False
            oqs = importlib.import_module("oqs")
            with oqs.Signature(mechanism) as verifier:
                try:
                    return bool(verifier.verify(bytes(message), bytes(signature), bytes(public_key)))
                except Exception:
                    return False

    @staticmethod
    def digest(message: bytes) -> bytes:
        return hashlib.sha3_256(message).digest()
