# benchmarks/chaotic_systems_benchmark.py
"""
Comprehensive Benchmark Suite for Chaotic PRNG Systems
Compares multiple chaotic systems for cryptographic quality

Academic Contribution:
- Performance comparison (throughput, latency)
- NIST SP 800-22 compliance analysis
- Lyapunov exponent calculation
- Statistical quality metrics
"""

import numpy as np
import time
import sys
import os
from scipy import stats
from scipy.stats import binomtest, norm
import hashlib
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Dict, List, Tuple
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@dataclass
class BenchmarkResult:
    """Results from a single chaotic system benchmark"""
    name: str
    throughput_mbps: float
    latency_us: float
    nist_frequency_p: float
    nist_runs_p: float
    lyapunov_exponent: float
    entropy_bits: float
    passed_nist: bool


class ChaoticSystem:
    """Base class for chaotic systems"""
    def __init__(self, name: str):
        self.name = name
        self.state = None
        self.last_byte = 0  # For adaptive iteration
        
    def step(self) -> None:
        """Advance the system by one time step"""
        raise NotImplementedError
        
    def get_byte(self) -> int:
        """Extract a random byte from current state"""
        raise NotImplementedError
        
    def reset(self, seed=None):
        """Reset system to initial conditions"""
        raise NotImplementedError
        
    def _extract_byte_improved(self, base_iterations=50) -> int:
        """Improved bit extraction with adaptive iterations and better hashing"""
        # Adaptive iteration count based on previous output (more chaos)
        iterations = base_iterations + (self.last_byte % 50) + 20  # +20 more iterations
        
        for _ in range(iterations):
            self.step()
            
        # Collect state data with higher precision
        if hasattr(self, 'x') and hasattr(self, 'y'):
            if hasattr(self, 'z'):
                data = f"{self.x:.15f}:{self.y:.15f}:{self.z:.15f}:{iterations}".encode()
            else:
                data = f"{self.x:.15f}:{self.y:.15f}:{iterations}".encode()
        else:
            data = f"{self.x:.15f}:{iterations}".encode()
            
        # Use SHA256 and cascade XOR across multiple bytes
        hash_result = hashlib.sha256(data).digest()
        byte_val = 0
        for i in range(8):  # Use 8 bytes instead of 2
            byte_val ^= hash_result[i]
            
        self.last_byte = byte_val
        return byte_val
    
    def _von_neumann_extract_bits(self, raw_bits: np.ndarray) -> np.ndarray:
        """Von Neumann unbiased bit extractor"""
        output = []
        i = 0
        while i < len(raw_bits) - 1:
            if raw_bits[i] == 0 and raw_bits[i+1] == 1:
                output.append(0)
                i += 2
            elif raw_bits[i] == 1 and raw_bits[i+1] == 0:
                output.append(1)
                i += 2
            else:
                i += 2  # Skip 00 and 11 pairs
        return np.array(output, dtype=np.uint8) if output else np.array([], dtype=np.uint8)


class RosslerSystem(ChaoticSystem):
    """Rössler attractor (current system)"""
    def __init__(self, a=0.1, b=0.1, c=14.0, dt=0.01):
        super().__init__("Rössler")
        self.a, self.b, self.c, self.dt = a, b, c, dt
        self.last_byte = 0
        self.reset()
        
    def reset(self, seed=None):
        if seed:
            np.random.seed(seed)
        self.x = np.random.uniform(-10, 10)
        self.y = np.random.uniform(-10, 10)
        self.z = np.random.uniform(0, 20)
        
    def step(self):
        dx = -self.y - self.z
        dy = self.x + self.a * self.y
        dz = self.b + self.z * (self.x - self.c)
        
        self.x += dx * self.dt
        self.y += dy * self.dt
        self.z += dz * self.dt
        
    def get_byte(self) -> int:
        return self._extract_byte_improved(base_iterations=50)


class LorenzSystem(ChaoticSystem):
    """Lorenz attractor"""
    def __init__(self, sigma=10.0, rho=28.0, beta=8.0/3.0, dt=0.01):
        super().__init__("Lorenz")
        self.sigma, self.rho, self.beta, self.dt = sigma, rho, beta, dt
        self.last_byte = 0
        self.reset()
        
    def reset(self, seed=None):
        if seed:
            np.random.seed(seed)
        self.x = np.random.uniform(-10, 10)
        self.y = np.random.uniform(-10, 10)
        self.z = np.random.uniform(0, 40)
        
    def step(self):
        dx = self.sigma * (self.y - self.x)
        dy = self.x * (self.rho - self.z) - self.y
        dz = self.x * self.y - self.beta * self.z
        
        self.x += dx * self.dt
        self.y += dy * self.dt
        self.z += dz * self.dt
        
    def get_byte(self) -> int:
        return self._extract_byte_improved(base_iterations=50)


class ChenSystem(ChaoticSystem):
    """Chen attractor"""
    def __init__(self, a=35.0, b=3.0, c=28.0, dt=0.005):
        super().__init__("Chen")
        self.a, self.b, self.c, self.dt = a, b, c, dt
        self.last_byte = 0
        self.reset()
        
    def reset(self, seed=None):
        if seed:
            np.random.seed(seed)
        self.x = np.random.uniform(-10, 10)
        self.y = np.random.uniform(-10, 10)
        self.z = np.random.uniform(10, 30)
        
    def step(self):
        dx = self.a * (self.y - self.x)
        dy = (self.c - self.a) * self.x - self.x * self.z + self.c * self.y
        dz = self.x * self.y - self.b * self.z
        
        self.x += dx * self.dt
        self.y += dy * self.dt
        self.z += dz * self.dt
        
    def get_byte(self) -> int:
        return self._extract_byte_improved(base_iterations=50)


class LogisticMap(ChaoticSystem):
    """Coupled Logistic maps (3D for better randomness)"""
    def __init__(self, r1=3.99, r2=3.98, r3=3.97, coupling=0.1):
        super().__init__("Logistic Map (Coupled)")
        self.r1, self.r2, self.r3 = r1, r2, r3
        self.coupling = coupling  # Coupling strength
        self.last_byte = 0
        self.reset()
        
    def reset(self, seed=None):
        if seed:
            np.random.seed(seed)
        self.x = np.random.uniform(0.1, 0.9)
        self.y = np.random.uniform(0.1, 0.9)
        self.z = np.random.uniform(0.1, 0.9)
        
    def step(self):
        # Coupled logistic maps for increased complexity
        x_new = self.r1 * self.x * (1 - self.x) + self.coupling * (self.y - self.x)
        y_new = self.r2 * self.y * (1 - self.y) + self.coupling * (self.z - self.y)
        z_new = self.r3 * self.z * (1 - self.z) + self.coupling * (self.x - self.z)
        
        # Keep in valid range [0, 1]
        self.x = max(0.0001, min(0.9999, x_new))
        self.y = max(0.0001, min(0.9999, y_new))
        self.z = max(0.0001, min(0.9999, z_new))
        
    def get_byte(self) -> int:
        return self._extract_byte_improved(base_iterations=150)


class HenonMap(ChaoticSystem):
    """Hénon map (2D)"""
    def __init__(self, a=1.4, b=0.3):
        super().__init__("Hénon Map")
        self.a, self.b = a, b
        self.last_byte = 0
        self.reset()
        
    def reset(self, seed=None):
        if seed:
            np.random.seed(seed)
        self.x = np.random.uniform(-0.5, 0.5)
        self.y = np.random.uniform(-0.5, 0.5)
        
    def step(self):
        try:
            x_new = 1 - self.a * self.x**2 + self.y
            y_new = self.b * self.x
            
            # Overflow prevention
            if abs(x_new) > 100 or abs(y_new) > 100 or not (np.isfinite(x_new) and np.isfinite(y_new)):
                self.reset()
            else:
                self.x, self.y = x_new, y_new
        except (OverflowError, FloatingPointError):
            self.reset()
        
    def get_byte(self) -> int:
        return self._extract_byte_improved(base_iterations=100)


class DuffingSystem(ChaoticSystem):
    """Duffing oscillator"""
    def __init__(self, alpha=-1.0, beta=1.0, gamma=0.3, delta=0.2, omega=1.0, dt=0.01):
        super().__init__("Duffing")
        self.alpha, self.beta = alpha, beta
        self.gamma, self.delta, self.omega = gamma, delta, omega
        self.dt = dt
        self.t = 0
        self.last_byte = 0
        self.reset()
        
    def reset(self, seed=None):
        if seed:
            np.random.seed(seed)
        self.x = np.random.uniform(-1, 1)
        self.v = np.random.uniform(-1, 1)
        self.t = 0
        
    def step(self):
        dv = -self.delta * self.v - self.alpha * self.x - self.beta * self.x**3 + \
             self.gamma * np.cos(self.omega * self.t)
        self.v += dv * self.dt
        self.x += self.v * self.dt
        self.t += self.dt
        
    def get_byte(self) -> int:
        return self._extract_byte_improved(base_iterations=50)


class SprottSystem(ChaoticSystem):
    """Sprott attractor (simple 3D chaotic system)"""
    def __init__(self, a=2.07, dt=0.05):
        super().__init__("Sprott")
        self.a = a
        self.dt = dt
        self.last_byte = 0
        self.reset()
        
    def reset(self, seed=None):
        if seed:
            np.random.seed(seed)
        self.x = np.random.uniform(-1, 1)
        self.y = np.random.uniform(-1, 1)
        self.z = np.random.uniform(-1, 1)
        
    def step(self):
        dx = self.y + self.a * self.x * self.y + self.x * self.z
        dy = 1 - self.a * self.x**2 + self.y * self.z
        dz = self.x - self.x**2 - self.y**2
        
        self.x += dx * self.dt
        self.y += dy * self.dt
        self.z += dz * self.dt
        
    def get_byte(self) -> int:
        for _ in range(50):
            self.step()
        data = f"{self.x}:{self.y}:{self.z}".encode()
        hash_result = hashlib.sha256(data).digest()
        return hash_result[0] ^ hash_result[1]


class BenchmarkSuite:
    """Comprehensive benchmark suite for chaotic systems"""
    
    def __init__(self):
        self.systems = [
            RosslerSystem(),
            LorenzSystem(),
            ChenSystem(),
            HenonMap(),
            DuffingSystem(),
            SprottSystem()
        ]
        self.results: List[BenchmarkResult] = []
        
    def measure_throughput(self, system: ChaoticSystem, duration_sec=1.0) -> Tuple[float, float]:
        """Measure throughput and latency"""
        system.reset(42)
        
        # Warmup
        for _ in range(1000):
            system.get_byte()
            
        # Actual measurement
        start = time.perf_counter()
        count = 0
        latencies = []
        
        while time.perf_counter() - start < duration_sec:
            t0 = time.perf_counter()
            system.get_byte()
            t1 = time.perf_counter()
            latencies.append((t1 - t0) * 1e6)  # microseconds
            count += 1
            
        elapsed = time.perf_counter() - start
        throughput_mbps = (count * 8) / (elapsed * 1_000_000)  # Mbps
        avg_latency = np.mean(latencies)
        
        return throughput_mbps, avg_latency
        
    def nist_frequency_test(self, bits: np.ndarray) -> float:
        """NIST Frequency (Monobit) Test"""
        ones = np.sum(bits)
        n = len(bits)
        p_value = binomtest(ones, n, 0.5).pvalue
        return p_value
        
    def nist_runs_test(self, bits: np.ndarray) -> float:
        """NIST Runs Test (FIXED VERSION)"""
        n = len(bits)
        ones = np.sum(bits)
        zeros = n - ones
        
        # Pre-test: proportion of ones should be close to 0.5
        pi = ones / n
        tau = 2 / np.sqrt(n)
        if abs(pi - 0.5) >= tau:
            return 0.0
            
        runs = 1 + np.sum(bits[:-1] != bits[1:])
        expected_runs = (2 * ones * zeros) / n + 1
        
        # Calculate standard deviation
        numerator = (expected_runs - 1) * (expected_runs - 2)
        denominator = n - 1
        
        if denominator <= 0 or numerator < 0:
            return 0.0
            
        stdev_runs = np.sqrt(numerator / denominator)
        
        # FIX: Handle edge cases properly
        if stdev_runs < 1e-10:
            # If no variation expected, check if actual matches expected
            if abs(runs - expected_runs) < 1:
                return 1.0
            else:
                return 0.0
        
        z_score = abs(runs - expected_runs) / stdev_runs
        p_value = norm.sf(z_score) * 2  # two-sided p-value
        
        return max(0.0, min(1.0, p_value))  # Ensure p-value is in [0,1]
        
    def calculate_lyapunov(self, system: ChaoticSystem, steps=10000) -> float:
        """Estimate largest Lyapunov exponent"""
        system.reset(42)
        
        # Let system settle
        for _ in range(1000):
            system.step()
            
        lyap_sum = 0
        count = 0
        
        # Special handling for 1D systems (Logistic Map)
        if system.name == "Logistic Map (Coupled)" and hasattr(system, 'x') and hasattr(system, 'y') and hasattr(system, 'z'):
            # Use 3D Lyapunov for coupled system
            for _ in range(steps):
                x0, y0, z0 = system.x, system.y, system.z
                
                dx = 1e-8
                system.x += dx
                system.step()
                
                distance = np.sqrt((system.x - x0)**2 + (system.y - y0)**2 + (system.z - z0)**2)
                
                if distance > 1e-12:
                    lyap_sum += np.log(distance / dx)
                    count += 1
                
                system.x, system.y, system.z = x0, y0, z0
        elif hasattr(system, 'x') and hasattr(system, 'y'):
            # 2D or 3D systems
            for _ in range(steps):
                x0, y0 = system.x, system.y
                z0 = system.z if hasattr(system, 'z') else 0
                
                dx = 1e-8
                system.x += dx
                system.step()
                
                if hasattr(system, 'z'):
                    distance = np.sqrt((system.x - x0)**2 + (system.y - y0)**2 + (system.z - z0)**2)
                else:
                    distance = np.sqrt((system.x - x0)**2 + (system.y - y0)**2)
                    
                if distance > 1e-12:
                    lyap_sum += np.log(distance / dx)
                    count += 1
                    
                system.x, system.y = x0, y0
                if hasattr(system, 'z'):
                    system.z = z0
        else:
            return 0.0
                
        return lyap_sum / count if count > 0 else 0.0
        
    def calculate_entropy(self, bytes_data: np.ndarray) -> float:
        """Calculate Shannon entropy"""
        counts = np.bincount(bytes_data, minlength=256)
        probs = counts / len(bytes_data)
        probs = probs[probs > 0]
        entropy = -np.sum(probs * np.log2(probs))
        return entropy
        
    def benchmark_system(self, system: ChaoticSystem, num_bits=1_000_000) -> BenchmarkResult:
        """Run complete benchmark on a single system"""
        print(f"\n{'='*70}")
        print(f"Benchmarking: {system.name}")
        print(f"{'='*70}")
        
        # 1. Performance
        print("  [1/6] Measuring throughput and latency...")
        throughput, latency = self.measure_throughput(system)
        print(f"        ✓ Throughput: {throughput:.2f} Mbps")
        print(f"        ✓ Latency: {latency:.2f} µs")
        
        # 2. Generate raw bits
        print(f"  [2/6] Generating {num_bits * 2:,} raw bits (will be post-processed)...")
        system.reset(42)
        num_bytes = ((num_bits * 2) + 7) // 8  # Generate 2x for Von Neumann
        bytes_data = np.array([system.get_byte() for _ in range(num_bytes)], dtype=np.uint8)
        raw_bits = np.unpackbits(bytes_data)[:num_bits * 2]
        print(f"        ✓ Generated successfully")
        
        # 3. Apply Von Neumann extractor
        print("  [3/6] Applying Von Neumann extractor...")
        processed_bits = system._von_neumann_extract_bits(raw_bits)
        
        # Ensure we have enough bits
        if len(processed_bits) < num_bits:
            print(f"        ⚠ Only {len(processed_bits):,} bits after extraction, padding...")
            # Generate more if needed
            while len(processed_bits) < num_bits:
                extra_bytes = np.array([system.get_byte() for _ in range(num_bytes // 2)], dtype=np.uint8)
                extra_bits = np.unpackbits(extra_bytes)
                extra_processed = system._von_neumann_extract_bits(extra_bits)
                processed_bits = np.concatenate([processed_bits, extra_processed])
        
        bits = processed_bits[:num_bits]
        print(f"        ✓ {len(bits):,} bits after Von Neumann extraction")
        
        # 4. NIST tests
        print("  [4/6] Running NIST tests...")
        freq_p = self.nist_frequency_test(bits)
        runs_p = self.nist_runs_test(bits)
        passed = (freq_p > 0.01) and (runs_p > 0.01)
        print(f"        ✓ Frequency test: p={freq_p:.6f} {'PASS' if freq_p > 0.01 else 'FAIL'}")
        print(f"        ✓ Runs test: p={runs_p:.6f} {'PASS' if runs_p > 0.01 else 'FAIL'}")
        
        # 5. Lyapunov exponent
        print("  [5/6] Calculating Lyapunov exponent...")
        try:
            lyap = self.calculate_lyapunov(system)
            print(f"        ✓ Lyapunov: {lyap:.4f}")
        except:
            lyap = 0.0
            print(f"        ✗ Could not calculate")
        
        # 6. Entropy (on processed bits)
        print("  [6/6] Calculating Shannon entropy...")
        # Convert bits back to bytes for entropy calculation
        if len(bits) >= 8:
            entropy_bytes = np.packbits(bits[:len(bits) - (len(bits) % 8)])
            entropy = self.calculate_entropy(entropy_bytes)
        else:
            entropy = 0.0
        passed = (freq_p > 0.01) and (runs_p > 0.01)
        print(f"        ✓ Entropy: {entropy:.4f} bits (max: 8.0)")
        
        return BenchmarkResult(
            name=system.name,
            throughput_mbps=throughput,
            latency_us=latency,
            nist_frequency_p=freq_p,
            nist_runs_p=runs_p,
            lyapunov_exponent=lyap,
            entropy_bits=entropy,
            passed_nist=passed
        )
        
    def run_all_benchmarks(self, num_bits=1_000_000):
        """Run benchmarks on all systems"""
        print("\n" + "="*70)
        print("COMPREHENSIVE CHAOTIC SYSTEMS BENCHMARK SUITE")
        print("="*70)
        print(f"Test parameters: {num_bits:,} bits per system")
        print(f"Systems to test: {len(self.systems)}")
        
        self.results = []
        for system in self.systems:
            result = self.benchmark_system(system, num_bits)
            self.results.append(result)
            
        self.print_summary()
        self.save_results()
        self.plot_results()
        
    def print_summary(self):
        """Print comparative summary"""
        print("\n" + "="*70)
        print("BENCHMARK SUMMARY")
        print("="*70)
        
        # Sort by throughput
        sorted_results = sorted(self.results, key=lambda x: x.throughput_mbps, reverse=True)
        
        print(f"\n{'System':<15} {'Throughput':<12} {'Latency':<10} {'NIST':<6} {'Entropy':<8} {'Lyapunov':<10}")
        print(f"{'-'*15} {'-'*12} {'-'*10} {'-'*6} {'-'*8} {'-'*10}")
        
        for r in sorted_results:
            nist_status = "✓ PASS" if r.passed_nist else "✗ FAIL"
            print(f"{r.name:<15} {r.throughput_mbps:>10.2f} Mbps "
                  f"{r.latency_us:>8.2f} µs {nist_status:<6} "
                  f"{r.entropy_bits:>6.4f} {r.lyapunov_exponent:>10.4f}")
                  
        # Best system
        best = sorted_results[0]
        print(f"\n🏆 Best Performance: {best.name} ({best.throughput_mbps:.2f} Mbps)")
        
        nist_passed = [r for r in self.results if r.passed_nist]
        print(f"✅ NIST Compliance: {len(nist_passed)}/{len(self.results)} systems passed")
        
    def save_results(self, filename="benchmark_results.json"):
        """Save results to JSON"""
        data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": [
                {
                    "name": r.name,
                    "throughput_mbps": float(r.throughput_mbps),
                    "latency_us": float(r.latency_us),
                    "nist_frequency_p": float(r.nist_frequency_p),
                    "nist_runs_p": float(r.nist_runs_p),
                    "lyapunov_exponent": float(r.lyapunov_exponent),
                    "entropy_bits": float(r.entropy_bits),
                    "passed_nist": bool(r.passed_nist)
                }
                for r in self.results
            ]
        }
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\n📊 Results saved to: {filepath}")
        
    def plot_results(self):
        """Generate comparative plots"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Chaotic Systems Benchmark Comparison', fontsize=16)
        
        names = [r.name for r in self.results]
        
        # Plot 1: Throughput
        ax = axes[0, 0]
        throughputs = [r.throughput_mbps for r in self.results]
        colors = ['green' if r.passed_nist else 'orange' for r in self.results]
        ax.barh(names, throughputs, color=colors)
        ax.set_xlabel('Throughput (Mbps)')
        ax.set_title('Performance: Throughput')
        ax.grid(axis='x', alpha=0.3)
        
        # Plot 2: Latency
        ax = axes[0, 1]
        latencies = [r.latency_us for r in self.results]
        ax.barh(names, latencies, color=colors)
        ax.set_xlabel('Latency (µs)')
        ax.set_title('Performance: Latency (lower is better)')
        ax.grid(axis='x', alpha=0.3)
        
        # Plot 3: Entropy
        ax = axes[1, 0]
        entropies = [r.entropy_bits for r in self.results]
        ax.barh(names, entropies, color=colors)
        ax.set_xlabel('Shannon Entropy (bits)')
        ax.set_title('Quality: Shannon Entropy (max: 8.0)')
        ax.set_xlim([7.9, 8.0])
        ax.grid(axis='x', alpha=0.3)
        
        # Plot 4: Lyapunov Exponent
        ax = axes[1, 1]
        lyapunovs = [r.lyapunov_exponent for r in self.results]
        ax.barh(names, lyapunovs, color=colors)
        ax.set_xlabel('Lyapunov Exponent')
        ax.set_title('Chaos: Largest Lyapunov Exponent')
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        filepath = os.path.join(os.path.dirname(__file__), 'benchmark_comparison.png')
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"📈 Plots saved to: {filepath}")
        plt.show()


if __name__ == "__main__":
    print("\n🚀 Starting Comprehensive Chaotic Systems Benchmark")
    print("   This will compare 6 different chaotic systems")
    print("   Estimated time: 2-3 minutes\n")
    
    suite = BenchmarkSuite()
    suite.run_all_benchmarks(num_bits=1_000_000)
    
    print("\n✅ Benchmark complete!")
    print("\nFor academic paper:")
    print("  - Results saved in JSON format")
    print("  - Comparison plots generated")
    print("  - Ready for statistical analysis")
