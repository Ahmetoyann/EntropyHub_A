# EntropyHub Validation Pack

Bu klasör, iki farklı doğrulama hattını içerir:

1. **Bağımsız doğrulama (istatistik + KEM tutarlılığı)**
2. **Bounded/formal doğrulama (özellik kontrolleri ve sözleşme doğrulaması)**

## 1) Bağımsız doğrulama

```bash
python tests/independent_validation.py
```

Üretilen rapor:

- `docs/verification/independent_validation_report.json`

Kontrol edilen metrikler:

- Shannon entropy (bits/byte)
- Monobit p-value
- Chi-square uniformity p-value
- Lag-1 autocorrelation
- KEM encaps/decaps success rate

## 2) Bounded / Formal doğrulama

```bash
python formal/entropyhub_bounded_formal.py
```

Bu script şunları bounded kapsamda doğrular:

- Sonlu alan üzerinde kapsülleme/açma eşitliği
- KEM giriş boyut sözleşmeleri
- XOR temporal mixing çıktı aralığı kapanışı (0..255)

### TLA+ Modeli

- `formal/EntropyHubKEM.tla`

Bu dosya, KEM durum makinesi için paylaşılmış sır eşitliği (`SharedSecretAgreement`) invariant'ını modeller; tam kriptografik güvenlik ispatı yerine davranışsal bir model sağlar.
