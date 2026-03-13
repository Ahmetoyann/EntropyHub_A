import json
import math
import os
import statistics
import sys
import time
from collections import Counter
from dataclasses import asdict, dataclass

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.chaos.nihde import NIHDE, RUST_CORE_AVAILABLE
from core.pqc.kyber768 import Kyber768


@dataclass
class EntropyHubRealBenchmark:
    timestamp: str 
    environment: dict
    rng: dict
    kem: dict


def shannon_entropy(byte_values: list[int]) -> float:
    n = len(byte_values)
    if n == 0:
        return 0.0
    counts = Counter(byte_values)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def monobit_p_value(bit_values: list[int]) -> float:
    n = len(bit_values)
    if n == 0:
        return 0.0
    ones = sum(bit_values)
    s_obs = abs(2 * ones - n) / math.sqrt(n)
    return math.erfc(s_obs / math.sqrt(2))


def runs_p_value(bit_values: list[int]) -> float:
    n = len(bit_values)
    if n < 2:
        return 0.0

    ones = sum(bit_values)
    pi = ones / n
    tau = 2 / math.sqrt(n)
    if abs(pi - 0.5) >= tau:
        return 0.0

    runs = 1
    for i in range(1, n):
        if bit_values[i] != bit_values[i - 1]:
            runs += 1

    denominator = 2 * math.sqrt(2 * n) * pi * (1 - pi)
    if denominator == 0:
        return 0.0

    return math.erfc(abs(runs - 2 * n * pi * (1 - pi)) / denominator)


def chi_square_uniform_p_value(byte_values: list[int]) -> float:
    n = len(byte_values)
    if n == 0:
        return 0.0
    expected = n / 256
    counts = [0] * 256
    for b in byte_values:
        counts[b] += 1

    chi2 = sum((c - expected) ** 2 / expected for c in counts)

    # Wilson-Hilferty approximation for chi-square upper-tail p-value
    k = 255.0
    z = ((chi2 / k) ** (1 / 3) - (1 - 2 / (9 * k))) / math.sqrt(2 / (9 * k))
    return 0.5 * math.erfc(z / math.sqrt(2))


def lag1_autocorr(byte_values: list[int]) -> float:
    if len(byte_values) < 2:
        return 0.0
    x = byte_values[:-1]
    y = byte_values[1:]
    mean_x = statistics.fmean(x)
    mean_y = statistics.fmean(y)

    num = sum((a - mean_x) * (b - mean_y) for a, b in zip(x, y))
    den_x = sum((a - mean_x) ** 2 for a in x)
    den_y = sum((b - mean_y) ** 2 for b in y)
    den = math.sqrt(den_x * den_y)
    return 0.0 if den == 0 else num / den


def unpack_bits(byte_values: list[int]) -> list[int]:
    bits = []
    for byte in byte_values:
        for shift in range(7, -1, -1):
            bits.append((byte >> shift) & 1)
    return bits


def benchmark_rng(sample_bytes: int = 200_000, latency_iterations: int = 10_000) -> dict:
    engine = NIHDE(use_live_qrng=False)

    for _ in range(500):
        engine.decide()

    latencies = []
    for _ in range(latency_iterations):
        t0 = time.perf_counter()
        engine.decide()
        t1 = time.perf_counter()
        latencies.append((t1 - t0) * 1e6)

    latency_us = statistics.fmean(latencies)
    latency_median = statistics.median(latencies)
    latency_min = min(latencies)
    latency_max = max(latencies)
    throughput_mbps = (8 / latency_us) if latency_us > 0 else 0.0

    t0 = time.perf_counter()
    bytes_out = [engine.decide() for _ in range(sample_bytes)]
    t1 = time.perf_counter()

    bits = unpack_bits(bytes_out)

    return {
        "sample_bytes": sample_bytes,
        "generation_time_s": t1 - t0,
        "throughput_mbps_estimated": throughput_mbps,
        "latency_us_mean": latency_us,
        "latency_us_median": latency_median,
        "latency_us_p95": float(statistics.quantiles(latencies, n=100)[94]),
        "latency_us_min": latency_min,
        "latency_us_max": latency_max,
        "entropy_bits_per_byte": shannon_entropy(bytes_out),
        "nist_frequency_p": monobit_p_value(bits),
        "nist_runs_p": runs_p_value(bits),
        "chi_square_uniform_p": chi_square_uniform_p_value(bytes_out),
        "lag1_autocorr": lag1_autocorr(bytes_out),
        "passes_basic_randomness": monobit_p_value(bits) > 0.01 and runs_p_value(bits) > 0.01,
    }


def benchmark_kem(trials: int = 1000) -> dict:
    keygen_us = []
    encaps_us = []
    decaps_us = []
    success = 0

    for _ in range(100):
        pk, sk = Kyber768.keygen()
        _, ct = Kyber768.encaps(pk)
        Kyber768.decaps(sk, ct)

    for _ in range(trials):
        t0 = time.perf_counter()
        pk, sk = Kyber768.keygen()
        t1 = time.perf_counter()

        ss_enc, ct = Kyber768.encaps(pk)
        t2 = time.perf_counter()

        ss_dec = Kyber768.decaps(sk, ct)
        t3 = time.perf_counter()

        keygen_us.append((t1 - t0) * 1e6)
        encaps_us.append((t2 - t1) * 1e6)
        decaps_us.append((t3 - t2) * 1e6)

        if ss_enc == ss_dec:
            success += 1

    return {
        "trials": trials,
        "success_rate": success / trials if trials else 0.0,
        "keygen_us_mean": statistics.fmean(keygen_us),
        "keygen_us_median": statistics.median(keygen_us),
        "encaps_us_mean": statistics.fmean(encaps_us),
        "encaps_us_median": statistics.median(encaps_us),
        "decaps_us_mean": statistics.fmean(decaps_us),
        "decaps_us_median": statistics.median(decaps_us),
        "keygen_us_p95": float(statistics.quantiles(keygen_us, n=100)[94]),
        "encaps_us_p95": float(statistics.quantiles(encaps_us, n=100)[94]),
        "decaps_us_p95": float(statistics.quantiles(decaps_us, n=100)[94]),
        "keygen_us_min": min(keygen_us),
        "encaps_us_min": min(encaps_us),
        "decaps_us_min": min(decaps_us),
        "keygen_us_max": max(keygen_us),
        "encaps_us_max": max(encaps_us),
        "decaps_us_max": max(decaps_us),
    }


def run_real_benchmark() -> EntropyHubRealBenchmark:
    rng_results = benchmark_rng(sample_bytes=200_000, latency_iterations=10_000)
    kem_results = benchmark_kem(trials=1000)

    env = {
        "python": sys.version,
        "rust_core_available": bool(RUST_CORE_AVAILABLE),
        "cwd": os.getcwd(),
    }

    return EntropyHubRealBenchmark(
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        environment=env,
        rng=rng_results,
        kem=kem_results,
    )


if __name__ == "__main__":
    result = run_real_benchmark()
    output_path = os.path.join(os.path.dirname(__file__), "benchmark_results_real.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(asdict(result), f, indent=2)

    print("=" * 80)
    print("ENTROPYHUB REAL BENCHMARK (MEASURED)")
    print("=" * 80)
    print(f"Timestamp: {result.timestamp}")
    print(f"Rust core available: {result.environment['rust_core_available']}")
    print("\n[RNG]")
    print(f"Latency mean (us): {result.rng['latency_us_mean']:.3f}")
    print(f"Latency median (us): {result.rng['latency_us_median']:.3f}")
    print(f"Throughput (Mbps): {result.rng['throughput_mbps_estimated']:.6f}")
    print(f"Entropy (bits/byte): {result.rng['entropy_bits_per_byte']:.6f}")
    print(f"NIST Frequency p: {result.rng['nist_frequency_p']:.6f}")
    print(f"NIST Runs p: {result.rng['nist_runs_p']:.6f}")
    print(f"Chi-square p: {result.rng['chi_square_uniform_p']:.6f}")
    print(f"Lag-1 autocorr: {result.rng['lag1_autocorr']:.6f}")
    print("\n[KEM]")
    print(f"Keygen mean (us): {result.kem['keygen_us_mean']:.3f}")
    print(f"Keygen median (us): {result.kem['keygen_us_median']:.3f}")
    print(f"Encaps mean (us): {result.kem['encaps_us_mean']:.3f}")
    print(f"Encaps median (us): {result.kem['encaps_us_median']:.3f}")
    print(f"Decaps mean (us): {result.kem['decaps_us_mean']:.3f}")
    print(f"Decaps median (us): {result.kem['decaps_us_median']:.3f}")
    print(f"Success rate: {result.kem['success_rate']*100:.2f}%")
    print(f"Saved: {output_path}")
