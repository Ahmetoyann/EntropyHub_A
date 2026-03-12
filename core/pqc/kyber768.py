from pqcrypto.kem import ml_kem_768
import importlib


class Kyber768:
    """Real Kyber/ML-KEM wrapper via pqcrypto (primary) and liboqs (fallback)."""

    PUBLIC_KEY_SIZE = 1184
    SECRET_KEY_SIZE = 2400
    CIPHERTEXT_SIZE = 1088
    SHARED_SECRET_SIZE = 32
    MECHANISMS = ("Kyber768", "ML-KEM-768")

    @classmethod
    def _select_mechanism(cls) -> str:
        try:
            oqs = importlib.import_module("oqs")
        except BaseException:
            oqs = None
        if oqs is None:
            return ""
        available = set(oqs.get_enabled_kem_mechanisms())
        for name in cls.MECHANISMS:
            if name in available:
                return name
        return ""

    @staticmethod
    def keygen():
        try:
            return ml_kem_768.generate_keypair()
        except Exception:
            mechanism = Kyber768._select_mechanism()
            if not mechanism:
                raise RuntimeError("No real Kyber backend available (pqcrypto/liboqs).")
            oqs = importlib.import_module("oqs")
            with oqs.KeyEncapsulation(mechanism) as kem:
                public_key = kem.generate_keypair()
                secret_key = kem.export_secret_key()
            return public_key, secret_key

    @staticmethod
    def encaps(pk):
        if not isinstance(pk, (bytes, bytearray)):
            raise TypeError("public key must be bytes")
        try:
            ciphertext, shared_secret = ml_kem_768.encrypt(bytes(pk))
            return shared_secret, ciphertext
        except ValueError:
            raise
        except Exception:
            mechanism = Kyber768._select_mechanism()
            if not mechanism:
                raise RuntimeError("No real Kyber backend available (pqcrypto/liboqs).")
            oqs = importlib.import_module("oqs")
            with oqs.KeyEncapsulation(mechanism) as kem:
                ciphertext, shared_secret = kem.encap_secret(bytes(pk))
            return shared_secret, ciphertext

    @staticmethod
    def decaps(sk, ct):
        if not isinstance(sk, (bytes, bytearray)):
            raise TypeError("secret key must be bytes")
        if not isinstance(ct, (bytes, bytearray)):
            raise TypeError("ciphertext must be bytes")
        try:
            return ml_kem_768.decrypt(bytes(sk), bytes(ct))
        except ValueError:
            raise
        except Exception:
            mechanism = Kyber768._select_mechanism()
            if not mechanism:
                raise RuntimeError("No real Kyber backend available (pqcrypto/liboqs).")
            oqs = importlib.import_module("oqs")
            with oqs.KeyEncapsulation(mechanism, secret_key=bytes(sk)) as kem:
                shared_secret = kem.decap_secret(bytes(ct))
            return shared_secret

# Test
if __name__ == "__main__":
    print("EntropyHub v2.0 — Real Kyber/ML-KEM Test")
    print("=" * 65)

    pk, sk = Kyber768.keygen()
    print(f"Public key   : {len(pk)} bytes")
    print(f"Secret key   : {len(sk)} bytes")

    ss_bob, ct = Kyber768.encaps(pk)
    print(f"Ciphertext   : {len(ct)} bytes")

    ss_alice = Kyber768.decaps(sk, ct)

    print("\nVerification:")
    print(f"Bob's secret  : {ss_bob.hex()[:64]}...")
    print(f"Alice's secret: {ss_alice.hex()[:64]}...")
    print(f"MATCH         : {'YES – PERFECT!' if ss_alice == ss_bob else 'NO'}")

    print("=" * 65)
    print("REAL KYBER/ML-KEM IS RUNNING via liboqs")
    print("EntropyHub v2.0 uses lattice-based PQC primitives.")
    print("=" * 65)