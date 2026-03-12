import sys
import os
import time
import numpy as np
from scipy.stats import binomtest, norm

# Set up the path to import NIHDE
# Assumes this script is in 'tests/' and project root is '../'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.chaos.nihde import NIHDE

NUM_BITS = 10_000_000
ALPHA = 0.01


def run_entropy_test(num_bits=NUM_BITS, alpha=ALPHA):
    engine = NIHDE(use_live_qrng=False)

    print("="*75)
    print("NIST SP 800-22 CORE COMPLIANCE TEST (Von Neumann Post-Processed)")
    print(f"Generating {num_bits:,} bits (Decisions)...")
    print("="*75)

    start_time = time.perf_counter()
    num_bytes = (num_bits + 7) // 8
    bytes_data = np.array([engine.decide() for _ in range(num_bytes)], dtype=np.uint8)
    bits = np.unpackbits(bytes_data)[:num_bits]
    end_time = time.perf_counter()

    ones = int(np.sum(bits))
    zeros = num_bits - ones
    latency = (end_time - start_time) / num_bits * 1e6

    print(f"-> Successfully generated {num_bits:,} bits | Latency: {latency:.2f} µs")
    print(f"-> Ones: {ones:,} ({ones/num_bits * 100:.3f}%) | Zeros: {zeros:,}")

    p_freq = binomtest(ones, num_bits, 0.5).pvalue
    runs = 1 + np.sum(bits[:-1] != bits[1:])
    expected_runs = (2 * ones * zeros) / num_bits + 1
    stdev_runs = np.sqrt((expected_runs - 1) * (expected_runs - 2) / (num_bits - 1))
    z_score = np.abs(runs - expected_runs) / stdev_runs
    p_runs = norm.sf(z_score) * 2

    print("\n" + "="*75)
    print(f"CORE NIST SP 800-22 TEST RESULTS (α = {alpha})")
    print("="*75)

    freq_status = "PASSED" if p_freq > alpha else "FAILED"
    runs_status = "PASSED" if p_runs > alpha else "FAILED"

    print(f"1. Frequency Test             -> {freq_status:6} (p = {p_freq:.6f})")
    print(f"2. Runs Test                  -> {runs_status:6} (p = {p_runs:.6f})")

    overall_passed = freq_status == "PASSED" and runs_status == "PASSED"
    print("\n" + "="*75)
    if overall_passed:
        print("CORE VALIDATION PASSED -> ENTROPYHUB OUTPUT MEETS FUNDAMENTAL CRITERIA.")
    else:
        print("CORE VALIDATION FAILED -> REVIEW CHAOS PARAMETERS AND POST-PROCESSING.")
    print("="*75)

    return {
        "p_freq": p_freq,
        "p_runs": p_runs,
        "passed": overall_passed,
    }


if __name__ == "__main__":
    run_entropy_test()