import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VERIFY_DIR = os.path.join(ROOT, "docs", "verification")
BENCH_FILE = os.path.join(ROOT, "benchmarks", "benchmark_results_real.json")
IND_FILE = os.path.join(VERIFY_DIR, "independent_validation_report.json")
FORMAL_FILE = os.path.join(VERIFY_DIR, "formal_bounded_report.json")
OUT_FILE = os.path.join(VERIFY_DIR, "TEKNOFEST_ENTROPYHUB_REPORT.md")


def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def fmt(v, digits=6):
    if isinstance(v, float):
        return f"{v:.{digits}f}"
    return str(v)


def build_report(bench, independent, formal):
    now = time.strftime("%Y-%m-%d %H:%M:%S")

    rng = bench.get("rng", {}) if bench else {}
    kem = bench.get("kem", {}) if bench else {}
    env = bench.get("environment", {}) if bench else {}

    lines = []
    lines.append("# EntropyHub Teknofest Teknik Raporu")
    lines.append("")
    lines.append(f"- Rapor zamanı: {now}")
    lines.append(f"- Benchmark kaynağı: `benchmarks/benchmark_results_real.json`")
    lines.append(f"- Bağımsız doğrulama kaynağı: `docs/verification/independent_validation_report.json`")
    lines.append(f"- Formal doğrulama kaynağı: `docs/verification/formal_bounded_report.json`")
    lines.append("")

    lines.append("## 1) Yürütme Özeti")
    lines.append("")
    if bench:
        lines.append(f"- Rust çekirdek aktif: **{env.get('rust_core_available')}**")
        lines.append(f"- RNG gecikme (ortalama): **{fmt(rng.get('latency_us_mean', 0), 3)} µs**")
        lines.append(f"- RNG throughput: **{fmt(rng.get('throughput_mbps_estimated', 0), 3)} Mbps**")
        lines.append(f"- Entropy: **{fmt(rng.get('entropy_bits_per_byte', 0), 6)} bits/byte**")
        lines.append(f"- KEM başarı oranı: **{fmt(kem.get('success_rate', 0) * 100, 2)}%**")
    else:
        lines.append("- Benchmark verisi bulunamadı.")
    lines.append("")

    lines.append("## 2) Ortam ve Metodoloji")
    lines.append("")
    if bench:
        lines.append(f"- Python: `{env.get('python', 'N/A')}`")
        lines.append(f"- Çalışma dizini: `{env.get('cwd', 'N/A')}`")
    lines.append("- RNG ölçümü: 10k latency iterasyonu + 200k byte kalite ölçümü")
    lines.append("- KEM ölçümü: 1000 trial (keygen/encaps/decaps)")
    lines.append("- İstatistik: mean/median/p95/min/max + NIST temel testleri")
    lines.append("")

    lines.append("## 3) RNG Gerçek Ölçüm Sonuçları")
    lines.append("")
    if bench:
        lines.append("| Metrik | Değer |")
        lines.append("|---|---:|")
        lines.append(f"| Latency mean (µs) | {fmt(rng.get('latency_us_mean', 0), 3)} |")
        lines.append(f"| Latency median (µs) | {fmt(rng.get('latency_us_median', 0), 3)} |")
        lines.append(f"| Latency p95 (µs) | {fmt(rng.get('latency_us_p95', 0), 3)} |")
        lines.append(f"| Throughput (Mbps) | {fmt(rng.get('throughput_mbps_estimated', 0), 6)} |")
        lines.append(f"| Entropy (bits/byte) | {fmt(rng.get('entropy_bits_per_byte', 0), 6)} |")
        lines.append(f"| NIST Frequency p | {fmt(rng.get('nist_frequency_p', 0), 6)} |")
        lines.append(f"| NIST Runs p | {fmt(rng.get('nist_runs_p', 0), 6)} |")
        lines.append(f"| Chi-square p | {fmt(rng.get('chi_square_uniform_p', 0), 6)} |")
        lines.append(f"| Lag-1 autocorr | {fmt(rng.get('lag1_autocorr', 0), 6)} |")
        lines.append(f"| Basic randomness pass | {rng.get('passes_basic_randomness', False)} |")
    else:
        lines.append("- Veri yok")
    lines.append("")

    lines.append("## 4) KEM Gerçek Ölçüm Sonuçları")
    lines.append("")
    if bench:
        lines.append("| Metrik | Değer |")
        lines.append("|---|---:|")
        lines.append(f"| Trials | {kem.get('trials', 0)} |")
        lines.append(f"| Success Rate | {fmt(kem.get('success_rate', 0) * 100, 2)}% |")
        lines.append(f"| Keygen mean (µs) | {fmt(kem.get('keygen_us_mean', 0), 3)} |")
        lines.append(f"| Encaps mean (µs) | {fmt(kem.get('encaps_us_mean', 0), 3)} |")
        lines.append(f"| Decaps mean (µs) | {fmt(kem.get('decaps_us_mean', 0), 3)} |")
        lines.append(f"| Keygen p95 (µs) | {fmt(kem.get('keygen_us_p95', 0), 3)} |")
        lines.append(f"| Encaps p95 (µs) | {fmt(kem.get('encaps_us_p95', 0), 3)} |")
        lines.append(f"| Decaps p95 (µs) | {fmt(kem.get('decaps_us_p95', 0), 3)} |")
    else:
        lines.append("- Veri yok")
    lines.append("")

    lines.append("## 5) Bağımsız Doğrulama")
    lines.append("")
    if independent:
        lines.append(f"- Durum: **{independent.get('status', 'N/A')}**")
        lines.append(f"- Çekirdek: `{independent.get('core_type', 'N/A')}` (rust={independent.get('rust_core_available', 'N/A')})")
        lines.append(f"- Entropy: {fmt(independent.get('entropy_bits_per_byte', 0), 6)}")
        lines.append(f"- Monobit p: {fmt(independent.get('monobit_p_value', 0), 6)}")
        lines.append(f"- Chi-square p: {fmt(independent.get('chi_square_p_value', 0), 6)}")
        lines.append(f"- Lag-1 autocorr: {fmt(independent.get('lag1_autocorr', 0), 6)}")
        lines.append(f"- KEM success: {fmt(independent.get('kem_success_rate', 0) * 100, 2)}%")
    else:
        lines.append("- Bağımsız doğrulama dosyası bulunamadı.")
    lines.append("")

    lines.append("## 6) Formal/Bağlı Doğrulama")
    lines.append("")
    if formal:
        lines.append(f"- Durum: **{formal.get('status', 'N/A')}**")
        checks = formal.get("checks", {})
        lines.append(f"- Bounded KEM domain size: {checks.get('bounded_kem_equivalence_domain_size', 'N/A')}")
        lines.append(f"- Input contract check: {checks.get('input_contract_check', False)}")
        lines.append(f"- RNG output range check: {checks.get('rng_output_range_check', False)}")
    else:
        lines.append("- Formal doğrulama dosyası bulunamadı.")
    lines.append("")

    lines.append("## 7) Yeniden Üretilebilirlik Komutları")
    lines.append("")
    lines.append("```bash")
    lines.append("python benchmarks/real_entropyhub_benchmark.py")
    lines.append("python tests/independent_validation.py")
    lines.append("python formal/entropyhub_bounded_formal.py")
    lines.append("python docs/verification/generate_teknofest_report.py")
    lines.append("```")
    lines.append("")

    lines.append("## 8) Kaynakça")
    lines.append("")
    lines.append("1. NIST SP 800-22 Rev.1a — Statistical Test Suite for Random and Pseudorandom Number Generators.")
    lines.append("2. NIST FIPS 203 — Module-Lattice-Based Key-Encapsulation Mechanism Standard (ML-KEM).")
    lines.append("3. Rössler, O. E. (1976). An equation for continuous chaos.")
    lines.append("4. EntropyHub kaynak kodu ve ölçüm artefaktları:")
    lines.append("   - `benchmarks/real_entropyhub_benchmark.py`")
    lines.append("   - `benchmarks/benchmark_results_real.json`")
    lines.append("   - `tests/independent_validation.py`")
    lines.append("   - `formal/entropyhub_bounded_formal.py`")
    lines.append("   - `formal/EntropyHubKEM.tla`")

    return "\n".join(lines) + "\n"


def main():
    bench = load_json(BENCH_FILE)
    independent = load_json(IND_FILE)
    formal = load_json(FORMAL_FILE)

    os.makedirs(VERIFY_DIR, exist_ok=True)
    content = build_report(bench, independent, formal)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Saved: {OUT_FILE}")


if __name__ == "__main__":
    main()
