# EntropyHub Blockchain Extensions (PoC)

Bu klasör, EntropyHub için acil blokzincir/PQC entegrasyon PoC'lerini içerir.

## İçerik

- `oracle_poc.py`: EntropyHub tabanlı off-chain oracle
- `dlt_layer.py`: EntropyHub-seeded proposer seçimi + Dilithium3 blok imzalama
- `contracts/EntropyHubOracle.sol`: Oracle sonuçlarını zincire yazan Solidity kontratı
- `contracts/EntropyConsumer.sol`: Oracle verisini tüketen örnek consumer kontratı

## 1) Oracle PoC (Chainlink-benzeri akış)

```bash
python blockchain/oracle_poc.py
```

Üretilen akış:

1. EntropyHub rastgele veri üretir
2. SHA3 commitment oluşturur
3. Commitment, Dilithium3 ile imzalanır
4. Zincire gönderilecek paket hazırlanır

## 2) DLT PoC

```bash
python blockchain/dlt_layer.py
```

Özellikler:

- EntropyHub RNG ile proposer seçimi
- Blok hash'i üzerinde Dilithium3 imzası
- Zincir bütünlüğü + imza doğrulama

## 3) Gerçek PQC Gereksinimi

Bu PoC'ler gerçek lattice-based mekanizmaları kullanır:

- Birincil backend: **pqcrypto**
- Opsiyonel fallback backend: **liboqs-python (`oqs`)**

- KEM: Kyber768 / ML-KEM-768
- Signature: Dilithium3 / ML-DSA-65

Kurulum:

```bash
pip install pqcrypto
pip install oqs
```

Not: `oqs` çalışması için sistemde uygun liboqs runtime gerekir.
