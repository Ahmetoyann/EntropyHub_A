# tests/nist_test_suite.py
"""
NIST SP 800-22 Statistical Test Suite Implementation
Tests for randomness quality of the EntropyHub PRNG
"""

import numpy as np
from scipy import special, stats
from collections import Counter
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.chaos.nihde import NIHDE


class NISTTestSuite:
    """Implementation of key NIST SP 800-22 statistical tests"""
    
    def __init__(self, engine=None):
        self.engine = engine or NIHDE()
        self.results = {}
        
    def generate_bitstring(self, num_bits):
        """Generate bitstring from PRNG"""
        num_bytes = (num_bits + 7) // 8
        bytes_data = bytes([self.engine.decide() for _ in range(num_bytes)])
        bitstring = ''.join(format(byte, '08b') for byte in bytes_data)
        return bitstring[:num_bits]
    
    def monobit_test(self, bitstring):
        """
        NIST Test 1: Frequency (Monobit) Test
        Tests the proportion of zeros and ones
        """
        n = len(bitstring)
        s = sum(1 if bit == '1' else -1 for bit in bitstring)
        s_obs = abs(s) / np.sqrt(n)
        p_value = special.erfc(s_obs / np.sqrt(2))
        
        return {
            'test': 'Monobit Test',
            'p_value': p_value,
            'passed': p_value >= 0.01,
            's_obs': s_obs
        }
    
    def block_frequency_test(self, bitstring, block_size=128):
        """
        NIST Test 2: Frequency Test within a Block
        Tests the proportion of ones within M-bit blocks
        """
        n = len(bitstring)
        num_blocks = n // block_size
        
        if num_blocks == 0:
            return {'test': 'Block Frequency Test', 'p_value': 0.0, 'passed': False}
        
        proportions = []
        for i in range(num_blocks):
            block = bitstring[i*block_size:(i+1)*block_size]
            pi = sum(1 for bit in block if bit == '1') / block_size
            proportions.append(pi)
        
        chi_squared = 4 * block_size * sum((pi - 0.5)**2 for pi in proportions)
        p_value = special.gammaincc(num_blocks / 2, chi_squared / 2)
        
        return {
            'test': 'Block Frequency Test',
            'p_value': p_value,
            'passed': p_value >= 0.01,
            'chi_squared': chi_squared,
            'num_blocks': num_blocks
        }
    
    def runs_test(self, bitstring):
        """
        NIST Test 3: Runs Test
        Tests the total number of runs (consecutive bits with same value)
        """
        n = len(bitstring)
        ones = bitstring.count('1')
        pi = ones / n
        
        # Pre-test: check if |pi - 0.5| < 2/sqrt(n)
        if abs(pi - 0.5) >= 2 / np.sqrt(n):
            return {'test': 'Runs Test', 'p_value': 0.0, 'passed': False}
        
        # Count runs
        runs = 1
        for i in range(1, n):
            if bitstring[i] != bitstring[i-1]:
                runs += 1
        
        p_value = special.erfc(abs(runs - 2*n*pi*(1-pi)) / (2*np.sqrt(2*n)*pi*(1-pi)))
        
        return {
            'test': 'Runs Test',
            'p_value': p_value,
            'passed': p_value >= 0.01,
            'runs': runs,
            'expected_runs': 2*n*pi*(1-pi)
        }
    
    def longest_run_test(self, bitstring):
        """
        NIST Test 4: Test for the Longest Run of Ones
        """
        n = len(bitstring)
        
        # Configure based on block size
        if n < 128:
            return {'test': 'Longest Run Test', 'p_value': 0.0, 'passed': False}
        elif n < 6272:
            M, K = 8, 3
            v_values = [1, 2, 3, 4]
            pi_values = [0.2148, 0.3672, 0.2305, 0.1875]
        elif n < 750000:
            M, K = 128, 5
            v_values = [4, 5, 6, 7, 8, 9]
            pi_values = [0.1174, 0.2430, 0.2493, 0.1752, 0.1027, 0.1124]
        else:
            M, K = 10000, 6
            v_values = [10, 11, 12, 13, 14, 15, 16]
            pi_values = [0.0882, 0.2092, 0.2483, 0.1933, 0.1208, 0.0675, 0.0727]
        
        N = n // M
        frequencies = [0] * (K + 1)
        
        for i in range(N):
            block = bitstring[i*M:(i+1)*M]
            max_run = 0
            current_run = 0
            
            for bit in block:
                if bit == '1':
                    current_run += 1
                    max_run = max(max_run, current_run)
                else:
                    current_run = 0
            
            # Classify run length
            for j, v in enumerate(v_values):
                if max_run <= v:
                    frequencies[j] += 1
                    break
            else:
                frequencies[K] += 1
        
        chi_squared = sum((frequencies[i] - N*pi_values[i])**2 / (N*pi_values[i]) 
                         for i in range(K+1) if N*pi_values[i] > 0)
        p_value = special.gammaincc(K / 2, chi_squared / 2)
        
        return {
            'test': 'Longest Run Test',
            'p_value': p_value,
            'passed': p_value >= 0.01,
            'chi_squared': chi_squared
        }
    
    def spectral_test(self, bitstring):
        """
        NIST Test 6: Discrete Fourier Transform (Spectral) Test
        Detects periodic features in the bit sequence
        """
        n = len(bitstring)
        x = np.array([1 if bit == '1' else -1 for bit in bitstring])
        
        # Compute DFT
        s = np.fft.fft(x)
        modulus = np.abs(s[:n//2])
        
        # Expected threshold
        tau = np.sqrt(np.log(1/0.05) * n)
        
        # Count peaks below threshold
        n0 = 0.95 * n / 2
        n1 = len([m for m in modulus if m < tau])
        
        d = (n1 - n0) / np.sqrt(n * 0.95 * 0.05 / 4)
        p_value = special.erfc(abs(d) / np.sqrt(2))
        
        return {
            'test': 'Spectral Test',
            'p_value': p_value,
            'passed': p_value >= 0.01,
            'peaks_below_threshold': n1,
            'expected_peaks': n0
        }
    
    def approximate_entropy_test(self, bitstring, m=10):
        """
        NIST Test 8: Approximate Entropy Test
        Compares the frequency of overlapping blocks
        """
        n = len(bitstring)
        
        def phi(m):
            patterns = {}
            for i in range(n):
                pattern = bitstring[i:i+m] if i+m <= n else bitstring[i:] + bitstring[:m-(n-i)]
                patterns[pattern] = patterns.get(pattern, 0) + 1
            
            phi_m = sum(count * np.log(count / n) for count in patterns.values())
            return phi_m / n
        
        phi_m = phi(m)
        phi_m_plus = phi(m + 1)
        
        apen = phi_m - phi_m_plus
        chi_squared = 2 * n * (np.log(2) - apen)
        p_value = special.gammaincc(2**(m-1), chi_squared / 2)
        
        return {
            'test': 'Approximate Entropy Test',
            'p_value': p_value,
            'passed': p_value >= 0.01,
            'apen': apen,
            'chi_squared': chi_squared
        }
    
    def cumulative_sums_test(self, bitstring):
        """
        NIST Test 9: Cumulative Sums Test
        Tests for random walk deviation
        """
        n = len(bitstring)
        x = np.array([1 if bit == '1' else -1 for bit in bitstring])
        
        # Forward cumulative sum
        s_forward = np.cumsum(x)
        z_forward = max(np.abs(s_forward))
        
        # Backward cumulative sum
        s_backward = np.cumsum(x[::-1])
        z_backward = max(np.abs(s_backward))
        
        # Compute p-values
        p_forward = self._compute_cusum_pvalue(z_forward, n)
        p_backward = self._compute_cusum_pvalue(z_backward, n)
        
        return {
            'test': 'Cumulative Sums Test',
            'p_value_forward': p_forward,
            'p_value_backward': p_backward,
            'passed': p_forward >= 0.01 and p_backward >= 0.01,
            'z_forward': z_forward,
            'z_backward': z_backward
        }
    
    def _compute_cusum_pvalue(self, z, n):
        """Helper for cumulative sums p-value calculation"""
        sum_a = 0
        start = int((-n/z + 1) / 4)
        end = int((n/z - 1) / 4)
        
        for k in range(start, end + 1):
            sum_a += (stats.norm.cdf((4*k+1)*z/np.sqrt(n)) - 
                     stats.norm.cdf((4*k-1)*z/np.sqrt(n)))
        
        sum_b = 0
        start = int((-n/z - 3) / 4)
        end = int((n/z - 1) / 4)
        
        for k in range(start, end + 1):
            sum_b += (stats.norm.cdf((4*k+3)*z/np.sqrt(n)) - 
                     stats.norm.cdf((4*k+1)*z/np.sqrt(n)))
        
        return 1 - sum_a + sum_b
    
    def run_all_tests(self, num_bits=100000):
        """Run all NIST tests"""
        print(f"\n{'='*80}")
        print(f"NIST SP 800-22 Statistical Test Suite")
        print(f"Testing {num_bits} bits from EntropyHub PRNG")
        print(f"{'='*80}\n")
        
        bitstring = self.generate_bitstring(num_bits)
        
        tests = [
            self.monobit_test,
            self.block_frequency_test,
            self.runs_test,
            self.longest_run_test,
            self.spectral_test,
            lambda bs: self.approximate_entropy_test(bs, m=10),
            self.cumulative_sums_test
        ]
        
        results = []
        for test_func in tests:
            result = test_func(bitstring)
            results.append(result)
            self._print_result(result)
        
        # Summary
        passed = sum(1 for r in results if r.get('passed', False))
        total = len(results)
        
        print(f"\n{'='*80}")
        print(f"SUMMARY: {passed}/{total} tests passed")
        print(f"Success Rate: {passed/total*100:.1f}%")
        print(f"{'='*80}\n")
        
        self.results = {
            'num_bits': num_bits,
            'tests': results,
            'passed': passed,
            'total': total,
            'success_rate': passed/total
        }
        
        return self.results
    
    def _print_result(self, result):
        """Pretty print test result"""
        test_name = result['test']
        passed = result.get('passed', False)
        status = "✓ PASS" if passed else "✗ FAIL"
        
        print(f"{test_name:.<50} {status}")
        
        if 'p_value' in result:
            print(f"  P-value: {result['p_value']:.6f}")
        if 'p_value_forward' in result:
            print(f"  P-value (forward): {result['p_value_forward']:.6f}")
            print(f"  P-value (backward): {result['p_value_backward']:.6f}")
        print()


if __name__ == "__main__":
    # Run NIST tests
    suite = NISTTestSuite()
    results = suite.run_all_tests(num_bits=100000)
    
    # Additional test with more bits
    print("\n" + "="*80)
    print("Running extended test with 1,000,000 bits...")
    print("="*80)
    suite_extended = NISTTestSuite()
    results_extended = suite_extended.run_all_tests(num_bits=1000000)
