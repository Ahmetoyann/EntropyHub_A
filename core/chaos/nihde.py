# core/chaos/nihde.py

import math
import os
import struct
import sys
import time
from collections import deque

# Add the project root directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    try:
        from entropyhub_core_rs import EntropyHubCore
    except ImportError:
        from entropyhub_core_rs import AetherCore as EntropyHubCore
    RUST_CORE_AVAILABLE = True
except ImportError as e:
    try:
        from aether_core_rs import AetherCore as EntropyHubCore
        RUST_CORE_AVAILABLE = True
    except ImportError:
        print(f"WARNING: Could not import entropyhub_core_rs: {e}")
        print(f"WARNING: Falling back to Python implementation (slower)")
        RUST_CORE_AVAILABLE = False
    
    # Python fallback implementation
    class EntropyHubCore:
        """Pure Python fallback for the Rössler chaotic system."""

        def __init__(self, x, y, z, a, b, c, dt):
            self.x = float(x)
            self.y = float(y)
            self.z = float(z)
            self.a = float(a)
            self.b = float(b)
            self.c = float(c)
            self.dt = float(dt)
            
        def reseed_rust(self, x, y, z):
            """Reseed the chaotic system"""
            self.x = float(x) if abs(x) > 0.01 else 1.0
            self.y = float(y) if abs(y) > 0.01 else 1.0
            self.z = float(z) if abs(z) > 0.01 else 1.0
            
        def decide_rust(self, iterations=50):
            """Generate random byte using Rössler system"""
            for _ in range(iterations):
                dx = -self.y - self.z
                dy = self.x + self.a * self.y
                dz = self.b + self.z * (self.x - self.c)
                
                self.x += dx * self.dt
                self.y += dy * self.dt
                self.z += dz * self.dt
                
                # Prevent overflow/underflow
                if abs(self.x) > 1000:
                    self.x = self.x % 100.0
                if abs(self.y) > 1000:
                    self.y = self.y % 100.0
                if abs(self.z) > 1000:
                    self.z = self.z % 100.0
                    
                # Check for NaN
                if not (math.isfinite(self.x) and math.isfinite(self.y) and math.isfinite(self.z)):
                    self.x, self.y, self.z = 1.0, 1.0, 1.0
                
            # Convert final state to byte
            combined = abs(self.x) + abs(self.y) + abs(self.z)
            if not math.isfinite(combined):
                combined = 42.0  # fallback value
            return int(combined * 1000) % 256


class NIHDE:
    """
    Nondeterministic High-Entropy Decision Engine (NIHDE).
    Optimized random number generator based on the Rössler chaotic system.
    Continuous Health Check (CHC) has been removed for maximum performance.
    """
    def __init__(self, use_live_qrng=False, reseed_interval=256, raw_iterations=50, verbose=False):
        # EntropyHub/Rössler stable parameters (a=0.1, b=0.1, c=14.0)
        self.core = EntropyHubCore(1.0, 1.0, 1.0, 0.1, 0.1, 14.0, 0.01)
        self.use_live_qrng = bool(use_live_qrng)
        self.reseed_interval = max(1, int(reseed_interval))
        self.raw_iterations = max(1, int(raw_iterations))
        self.verbose = bool(verbose)

        # Reseed and runtime counters
        self.reseed_count = 0
        self.generated_raw_bytes = 0
        self.generated_output_bytes = 0
        self.last_reseed_timestamp = None
        self.last_reseed_source = "startup"
        self._raw_bit_buffer = deque()
        self._postprocessed_bits = deque()

        if self.use_live_qrng:
            self.reseed_manual(source="live_entropy")

    # Manual reseed method is kept for external calls if needed.
    def reseed_manual(self, source="manual"):
        """Reseed the system using OS entropy."""
        try:
            random_data = os.urandom(24)
            
            raw_x = struct.unpack('<d', random_data[0:8])[0]
            raw_y = struct.unpack('<d', random_data[8:16])[0]
            raw_z = struct.unpack('<d', random_data[16:24])[0]

            # Normalize to the [-100.0, 100.0) range
            new_x = (abs(raw_x) % 200.0) - 100.0
            new_y = (abs(raw_y) % 200.0) - 100.0
            new_z = (abs(raw_z) % 200.0) - 100.0
            
            # Prevent overly small initial values
            if abs(new_x) < 0.1: new_x += 0.1 
            if abs(new_y) < 0.1: new_y += 0.1
            if abs(new_z) < 0.1: new_z += 0.1

            self.core.reseed_rust(new_x, new_y, new_z)
            self.reseed_count += 1
            self.last_reseed_timestamp = time.time()
            self.last_reseed_source = source
            self._raw_bit_buffer.clear()
            self._postprocessed_bits.clear()
            if self.verbose:
                print(f"[INFO] System reseeded from {source} (Count: {self.reseed_count}).")
        
        except Exception as e:
            if self.verbose:
                print(f"[CRITICAL] Manual reseeding failed: {e}")


    @staticmethod
    def _byte_to_bits(value):
        return [(value >> shift) & 1 for shift in range(7, -1, -1)]

    def _raw_byte(self):
        if self.use_live_qrng and self.generated_raw_bytes > 0 and self.generated_raw_bytes % self.reseed_interval == 0:
            self.reseed_manual(source="live_entropy")

        self.generated_raw_bytes += 1
        return self.core.decide_rust(iterations=self.raw_iterations)

    def _fill_postprocessed_bits(self, target_bits=8):
        while len(self._postprocessed_bits) < target_bits:
            raw_byte = self._raw_byte()
            self._raw_bit_buffer.extend(self._byte_to_bits(raw_byte))

            while len(self._raw_bit_buffer) >= 2:
                first_bit = self._raw_bit_buffer.popleft()
                second_bit = self._raw_bit_buffer.popleft()

                if first_bit == 0 and second_bit == 1:
                    self._postprocessed_bits.append(0)
                elif first_bit == 1 and second_bit == 0:
                    self._postprocessed_bits.append(1)


    def decide_raw(self):
        """Return a raw byte before Von Neumann post-processing."""
        return self._raw_byte()


    def decide(self):
        """Return one post-processed byte using Von Neumann extraction."""
        self._fill_postprocessed_bits(target_bits=8)

        final_output = 0
        for _ in range(8):
            final_output = (final_output << 1) | self._postprocessed_bits.popleft()

        self.generated_output_bytes += 1
        return final_output

    def profile(self):
        return {
            "rust_core_available": bool(RUST_CORE_AVAILABLE),
            "use_live_qrng": self.use_live_qrng,
            "reseed_interval": self.reseed_interval,
            "raw_iterations": self.raw_iterations,
            "verbose": self.verbose,
            "reseed_count": self.reseed_count,
            "generated_raw_bytes": self.generated_raw_bytes,
            "generated_output_bytes": self.generated_output_bytes,
            "postprocessing": "von_neumann",
            "last_reseed_source": self.last_reseed_source,
            "last_reseed_timestamp": self.last_reseed_timestamp,
        }

    def get_attractor(self, num_points):
        """Generate chaotic attractor trajectory for visualization"""
        trajectory = []
        
        # Reseed for fresh trajectory
        self.reseed_manual(source="attractor")
        
        # Generate trajectory
        for _ in range(num_points):
            # Evolve the system
            self.core.decide_rust(iterations=1)
            
            # Store current state
            if RUST_CORE_AVAILABLE:
                # For Rust implementation, we have direct access to x, y, z
                trajectory.append([self.core.x, self.core.y, self.core.z])
            else:
                # For Python implementation, we have direct access
                trajectory.append([self.core.x, self.core.y, self.core.z])
        
        try:
            import numpy as np
            return np.array(trajectory)
        except ImportError:
            return trajectory
