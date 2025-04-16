"""
NIST statistical test suite for evaluating cryptographic randomness.
Implementation of key tests from NIST SP 800-22.
"""
import numpy as np
import math
import scipy.special as spc
from scipy.stats import chi2


class NISTTests:
    """
    Implementation of statistical tests from NIST SP 800-22 for
    evaluating the randomness of binary sequences used in cryptography.
    """
    
    @staticmethod
    def monobit_test(binary_data, significance_level=0.01):
        """
        Frequency (Monobit) Test - tests the proportion of zeros and ones.
        
        Args:
            binary_data: Binary sequence as bytes, bytearray or list of bits
            significance_level: Alpha threshold for P-value
            
        Returns:
            dict: Test results including P-value and success status
        """
        # Convert to ±1
        if isinstance(binary_data, (bytes, bytearray)):
            # Convert bytes to bit array
            bits = []
            for byte in binary_data:
                for i in range(8):
                    bits.append((byte >> i) & 1)
        else:
            bits = binary_data
            
        n = len(bits)
        
        # No data
        if n == 0:
            return {"name": "Monobit Test",
                    "p_value": 0.0,
                    "success": False,
                    "error": "Insufficient data length"
                   }
            
        # Convert bits to +1/-1
        s = 0
        for bit in bits:
            s += 2 * bit - 1
            
        # Calculate test statistic
        s_obs = abs(s) / math.sqrt(n)
        
        # Calculate P-value
        p_value = math.erfc(s_obs / math.sqrt(2))
        
        return {
            "name": "Monobit Test",
            "p_value": p_value,
            "success": p_value >= significance_level,
            "s_obs": s_obs,
            "bits": n
        }
        
    @staticmethod
    def block_frequency_test(binary_data, block_size=128, significance_level=0.01):
        """
        Block Frequency Test - tests the proportion of ones in blocks.
        
        Args:
            binary_data: Binary sequence as bytes, bytearray or list of bits
            block_size: Size of each block to analyze
            significance_level: Alpha threshold for P-value
            
        Returns:
            dict: Test results including P-value and success status
        """
        # Convert to bits if needed
        if isinstance(binary_data, (bytes, bytearray)):
            # Convert bytes to bit array
            bits = []
            for byte in binary_data:
                for i in range(8):
                    bits.append((byte >> i) & 1)
        else:
            bits = binary_data
            
        n = len(bits)
        
        # Check for sufficient data
        if n < block_size:
            return {
                "name": "Block Frequency Test",
                "p_value": 0.0,
                "success": False,
                "error": "Insufficient data for block size"
            }
            
        # Number of blocks (ensure complete blocks only)
        num_blocks = n // block_size

        # Process blocks
        block_sums = []
        for i in range(num_blocks):
            block = bits[i * block_size:(i + 1) * block_size]
            proportion = sum(block) / block_size
            block_sums.append(proportion)

        # Calculate chi-square
        chi_squared = 4.0 * block_size * sum((x - 0.5)**2 for x in block_sums)

        # Calculate P-value using the complementary incomplete gamma function
        # This is the correct way according to NIST SP 800-22
        p_value = spc.gammaincc(num_blocks / 2, chi_squared / 2)

        return {
            "name": "Block Frequency Test",
            "p_value": p_value,
            "success": p_value >= significance_level,
            "chi_squared": chi_squared,
            "blocks": num_blocks,
            "block_size": block_size
        }

    @staticmethod
    def runs_test(binary_data, significance_level=0.01):
        """
        Runs Test - tests oscillation between zeros and ones.

        Args:
            binary_data: Binary sequence as bytes, bytearray or list of bits
            significance_level: Alpha threshold for P-value

        Returns:
            dict: Test results including P-value and success status
        """
        # Convert to bits if needed
        if isinstance(binary_data, (bytes, bytearray)):
            # Convert bytes to bit array
            bits = []
            for byte in binary_data:
                for i in range(8):
                    bits.append((byte >> i) & 1)
        else:
            bits = binary_data

        n = len(bits)

        # Check for sufficient data
        if n < 100:
            return {
                "name": "Runs Test",
                "p_value": 0.0,
                "success": False,
                "error": "Insufficient data length"
            }

        # Calculate proportion of ones
        pi = sum(bits) / n

        # Check if proportion is valid for this test
        if abs(pi - 0.5) >= (2 / math.sqrt(n)):
            return {
                "name": "Runs Test",
                "p_value": 0.0,
                "success": False,
                "error": "Prerequisite monobit test failed"
            }

        # Count runs
        runs = 1
        for i in range(1, n):
            if bits[i] != bits[i-1]:
                runs += 1

        # Calculate test statistic
        r_obs = abs(runs - 2 * n * pi * (1 - pi)) / (2 * math.sqrt(n) * pi * (1 - pi))

        # Calculate P-value
        p_value = math.erfc(r_obs / math.sqrt(2))

        return {
            "name": "Runs Test",
            "p_value": p_value,
            "success": p_value >= significance_level,
            "runs": runs,
            "pi": pi
        }

    @staticmethod
    def longest_run_ones_test(binary_data, significance_level=0.01):
        """
        Longest Run of Ones Test - tests the length of the longest run of ones.

        Args:
            binary_data: Binary sequence as bytes or list of bits
            significance_level: Alpha threshold for P-value

        Returns:
            dict: Test results including P-value and success status
        """
        # Convert to bits if needed
        if isinstance(binary_data, (bytes, bytearray)):
            # Convert bytes to bit array
            bits = []
            for byte in binary_data:
                for i in range(8):
                    bits.append((byte >> i) & 1)
        else:
            bits = binary_data

        n = len(bits)

        # Determine parameters based on sequence length
        if n < 128:
            return {
                "name": "Longest Run of Ones Test",
                "p_value": 0.0,
                "success": False,
                "error": "Insufficient data length"
            }
        elif n < 6272:
            M = 8  # Block size
            K = 3  # Number of categories
            # Expected probabilities for each category
            pi = [0.2148, 0.3672, 0.2305, 0.1875]
            # Category boundaries (inclusive-exclusive ranges)
            v_categories = [0, 1, 2, 3, 4]  # 0, 1, 2, 3, ≥4
        elif n < 750000:
            M = 128
            K = 5
            pi = [0.1174, 0.2430, 0.2493, 0.1752, 0.1027, 0.1124]
            v_categories = [0, 1, 2, 3, 4, 5, 6, 7, 8]  # 0-1, 2-3, 4, 5, 6-7, ≥8
        else:
            M = 10000
            K = 6
            pi = [0.0882, 0.2092, 0.2483, 0.1933, 0.1208, 0.0675, 0.0727]
            v_categories = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]  # Expanded categories

        # Number of blocks
        N = n // M

        # Initialize frequency counts
        v = [0] * len(pi)

        # Find longest run in each block
        for i in range(N):
            block = bits[i * M:(i + 1) * M]

            # Find longest run in the block
            longest = 0
            current_run = 0
            for bit in block:
                if bit == 1:
                    current_run += 1
                    longest = max(longest, current_run)
                else:
                    current_run = 0

            # Categorize the longest run based on length
            if n < 6272:  # For smaller sequences
                if longest <= 1:
                    v[0] += 1
                elif longest == 2:
                    v[1] += 1
                elif longest == 3:
                    v[2] += 1
                else:  # longest >= 4
                    v[3] += 1
            elif n < 750000:  # For medium sequences
                if longest <= 1:
                    v[0] += 1
                elif longest <= 3:
                    v[1] += 1
                elif longest == 4:
                    v[2] += 1
                elif longest == 5:
                    v[3] += 1
                elif longest <= 7:
                    v[4] += 1
                else:  # longest >= 8
                    v[5] += 1
            else:  # For long sequences
                if longest <= 1:
                    v[0] += 1
                elif longest <= 3:
                    v[1] += 1
                elif longest <= 6:
                    v[2] += 1
                elif longest <= 10:
                    v[3] += 1
                elif longest <= 16:
                    v[4] += 1
                elif longest <= 22:
                    v[5] += 1
                else:  # longest > 22
                    v[6] += 1

        # Calculate chi-squared
        chi_squared = sum((v[i] - N * pi[i]) ** 2 / (N * pi[i]) for i in range(len(pi)))

        # Calculate P-value
        p_value = spc.gammaincc(K / 2, chi_squared / 2)

        return {
            "name": "Longest Run of Ones Test",
            "p_value": p_value,
            "success": p_value >= significance_level,
            "chi_squared": chi_squared,
            "observed_frequencies": v,
            "expected_frequencies": [N * prob for prob in pi],
            "block_size": M,
            "num_blocks": N
        }

    @staticmethod
    def dft_test(binary_data, significance_level=0.01):
        """
        Discrete Fourier Transform Test - detects periodic features.

        Args:
            binary_data: Binary sequence as bytes or list of bits
            significance_level: Alpha threshold for P-value

        Returns:
            dict: Test results including P-value and success status
        """
        # Convert to bits if needed
        if isinstance(binary_data, (bytes, bytearray)):
            # Convert bytes to bit array
            bits = []
            for byte in binary_data:
                for i in range(8):
                    bits.append((byte >> i) & 1)
        else:
            bits = binary_data

        n = len(bits)

        # Check for sufficient data
        if n < 1000:
            return {
                "name": "DFT Test",
                "p_value": 0.0,
                "success": False,
                "error": "Insufficient data length"
            }

        # Convert to ±1
        x = [2 * bit - 1 for bit in bits]

        # Apply DFT
        S = np.fft.fft(x)
        modulus = np.abs(S[0:n//2])

        # Calculate threshold
        T = math.sqrt(math.log(1/0.05) * n)

        # Count values below threshold
        N0 = 0.95 * n / 2
        N1 = sum(1 for m in modulus if m < T)

        # Calculate test statistic
        d = (N1 - N0) / math.sqrt(n * 0.95 * 0.05 / 4)

        # Calculate P-value
        p_value = math.erfc(abs(d) / math.sqrt(2))

        return {
            "name": "DFT Test",
            "p_value": p_value,
            "success": p_value >= significance_level,
            "threshold": T,
            "expected_below": N0,
            "observed_below": N1
        }

    @staticmethod
    def serial_test(binary_data, block_size=16, significance_level=0.01):
        """
        Serial Test - tests uniformity of patterns of given length.

        Args:
            binary_data: Binary sequence as bytes or list of bits
            block_size: Size of patterns to test (m value)
            significance_level: Alpha threshold for P-value

        Returns:
            dict: Test results including P-values and success status
        """
        # Convert to bits if needed
        if isinstance(binary_data, (bytes, bytearray)):
            # Convert bytes to bit array
            bits = []
            for byte in binary_data:
                for i in range(8):
                    bits.append((byte >> i) & 1)
        else:
            bits = binary_data

        n = len(bits)

        # Check for sufficient data and valid block size
        if n < 2**(block_size+1) or block_size < 2:
            return {
                "name": "Serial Test",
                "p_value1": 0.0,
                "p_value2": 0.0,
                "success": False,
                "error": "Insufficient data or invalid block size"
            }

        # Create padded sequence for proper wrap-around
        padded_bits = bits + bits[:block_size-1]

        # Helper function to count patterns of a specific length
        def count_patterns(bits, pattern_length):
            counts = np.zeros(2**pattern_length, dtype=int)
            for i in range(n):
                pattern = 0
                for j in range(pattern_length):
                    pattern = (pattern << 1) | bits[(i + j) % n]
                counts[pattern] += 1
            return counts

        # Count patterns for m, m-1, and m-2
        counts_m = count_patterns(bits, block_size)
        counts_m1 = count_patterns(bits, block_size - 1)
        counts_m2 = count_patterns(bits, block_size - 2)

        # Calculate psi-square statistics
        psi_sq_m = np.sum(counts_m**2) * (2**block_size / n) - n
        psi_sq_m1 = np.sum(counts_m1**2) * (2**(block_size-1) / n) - n
        psi_sq_m2 = np.sum(counts_m2**2) * (2**(block_size-2) / n) - n

        # Calculate deltas
        delta1 = psi_sq_m - psi_sq_m1
        delta2 = psi_sq_m - 2 * psi_sq_m1 + psi_sq_m2

        # Calculate P-values using the correct degrees of freedom
        p_value1 = spc.gammaincc(2**(block_size-1) / 2, delta1 / 2)
        p_value2 = spc.gammaincc(2**(block_size-2) / 2, delta2 / 2)

        return {
            "name": "Serial Test",
            "p_value1": p_value1,
            "p_value2": p_value2,
            "success": p_value1 >= significance_level and p_value2 >= significance_level,
            "delta1": delta1,
            "delta2": delta2,
            "block_size": block_size,
            "degrees_of_freedom1": 2**(block_size-1),
            "degrees_of_freedom2": 2**(block_size-2)
        }

    @staticmethod
    def approximate_entropy_test(binary_data, block_size=10, significance_level=0.01):
        """
        Approximate Entropy Test - compares frequencies of overlapping patterns.

        Args:
            binary_data: Binary sequence as bytes or list of bits
            block_size: Size of blocks for comparison (m value)
            significance_level: Alpha threshold for P-value

        Returns:
            dict: Test results including P-value and success status
        """
        # Convert to bits if needed
        if isinstance(binary_data, (bytes, bytearray)):
            # Convert bytes to bit array
            bits = []
            for byte in binary_data:
                for i in range(8):
                    bits.append((byte >> i) & 1)
        else:
            bits = binary_data

        n = len(bits)

        # Check for sufficient data
        if n < 100:
            return {
                "name": "Approximate Entropy Test",
                "p_value": 0.0,
                "success": False,
                "error": "Insufficient data length"
            }

        # Function to calculate ApEn for a given pattern length
        def compute_frequency(m):
            # Initialize counts for all possible patterns
            counts = np.zeros(2**m)

            # Count each pattern occurrence
            for i in range(n):
                pattern = 0
                for j in range(m):
                    bit = bits[(i + j) % n]  # Proper wrap-around
                    pattern = (pattern << 1) | bit
                counts[pattern] += 1

            # Calculate probabilities and phi value
            probabilities = counts / n
            # Avoid log(0) by only summing where probability > 0
            return sum(p * np.log(p) for p in probabilities if p > 0)

        # Calculate phi values for m and m+1
        phi_m = compute_frequency(block_size)
        phi_m1 = compute_frequency(block_size + 1)

        # Calculate approximate entropy
        apen = phi_m - phi_m1

        # Calculate chi-squared statistic
        chi_squared = 2 * n * (np.log(2) - apen)

        # Calculate P-value using the correct degrees of freedom
        p_value = spc.gammaincc(2**(block_size-1), chi_squared / 2)

        return {
            "name": "Approximate Entropy Test",
            "p_value": p_value,
            "success": p_value >= significance_level,
            "chi_squared": chi_squared,
            "apen": apen,
            "block_size": block_size,
            "degrees_of_freedom": 2**(block_size-1)
        }

    @staticmethod
    def cumulative_sums_test(binary_data, significance_level=0.01):
        """
        Cumulative Sums Test - tests if cumulative sum of partial sequences is too large or too small.

        Args:
            binary_data: Binary sequence as bytes or list of bits
            significance_level: Alpha threshold for P-value

        Returns:
            dict: Test results including P-values and success status
        """
        # Convert to bits if needed
        if isinstance(binary_data, (bytes, bytearray)):
            # Convert bytes to bit array
            bits = []
            for byte in binary_data:
                for i in range(8):
                    bits.append((byte >> i) & 1)
        else:
            bits = binary_data

        n = len(bits)

        # Convert to ±1
        x = [2 * bit - 1 for bit in bits]

        # Mode 0 (forward)
        S = np.cumsum(x)
        z = max(abs(S))

        # Calculate P-value for forward
        p_value_forward = 0
        for k in range(-int(z//4), int(z//4) + 1):
            p_value_forward += math.exp(-((4*k+1) * z)**2 / (2 * n))
            p_value_forward += math.exp(-((4*k-1) * z)**2 / (2 * n))

        p_value_forward = 1 - p_value_forward

        # Mode 1 (backward)
        S_rev = np.cumsum(x[::-1])
        z_rev = max(abs(S_rev))

        # Calculate P-value for backward
        p_value_backward = 0
        for k in range(-int(z_rev//4), int(z_rev//4) + 1):
            p_value_backward += math.exp(-((4*k+1) * z_rev)**2 / (2 * n))
            p_value_backward += math.exp(-((4*k-1) * z_rev)**2 / (2 * n))

        p_value_backward = 1 - p_value_backward

        return {
            "name": "Cumulative Sums Test",
            "p_value_forward": p_value_forward,
            "p_value_backward": p_value_backward,
            "success": p_value_forward >= significance_level and p_value_backward >= significance_level,
            "z_forward": z,
            "z_backward": z_rev
        }

    @staticmethod
    def test_randomness(binary_data, significance_level=0.01):
        """
        Run all available statistical tests on a binary sequence.

        Args:
            binary_data: Binary sequence as bytes, bytearray, or list of bits
            significance_level: Alpha threshold for P-values

        Returns:
            dict: Results of all tests
        """
        results = {}

        # Run each test and collect results
        results["monobit"] = NISTTests.monobit_test(binary_data, significance_level)
        results["block_frequency"] = NISTTests.block_frequency_test(binary_data, significance_level=significance_level)
        results["runs"] = NISTTests.runs_test(binary_data, significance_level)
        results["longest_run"] = NISTTests.longest_run_ones_test(binary_data, significance_level)
        results["dft"] = NISTTests.dft_test(binary_data, significance_level)
        results["serial"] = NISTTests.serial_test(binary_data, significance_level=significance_level)
        results["approximate_entropy"] = NISTTests.approximate_entropy_test(binary_data, significance_level=significance_level)
        results["cumulative_sums"] = NISTTests.cumulative_sums_test(binary_data, significance_level)

        # Calculate overall success rate
        passed_tests = sum(1 for test in results.values() if test.get("success", False))
        total_tests = len(results)

        return {
            "results": results,
            "passed": passed_tests,
            "total": total_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "overall_success": passed_tests == total_tests
        }

    @staticmethod
    def bytes_to_bits(data):
        """Convert bytes to a list of bits."""
        bits = []
        for byte in data:
            for i in range(8):
                bits.append((byte >> i) & 1)
        return bits

    @staticmethod
    def summarize_results(test_results, verbose=False):
        """
        Generate a human-readable summary of test results.

        Args:
            test_results: Results from test_randomness()
            verbose: Whether to include detailed information

        Returns:
            str: Formatted summary of results
        """
        summary = []
        summary.append("NIST Statistical Test Suite Summary")
        summary.append("=" * 40)

        # Overall results
        summary.append(f"Tests passed: {test_results['passed']}/{test_results['total']} " +
                       f"({test_results['success_rate']*100:.1f}%)")
        summary.append(f"Overall assessment: " +
                       ("PASS" if test_results['overall_success'] else "FAIL"))
        summary.append("")

        # Individual test results
        summary.append("Individual Test Results:")
        summary.append("-" * 40)

        for name, result in test_results['results'].items():
            test_name = result.get("name", name.replace("_", " ").title())
            success = result.get("success", False)

            summary.append(f"{test_name}: {'PASS' if success else 'FAIL'}")

            if "p_value" in result:
                summary.append(f"  P-value: {result['p_value']:.6f}")
            elif "p_value1" in result and "p_value2" in result:
                summary.append(f"  P-value1: {result['p_value1']:.6f}")
                summary.append(f"  P-value2: {result['p_value2']:.6f}")
            elif "p_value_forward" in result and "p_value_backward" in result:
                summary.append(f"  P-value Forward: {result['p_value_forward']:.6f}")
                summary.append(f"  P-value Backward: {result['p_value_backward']:.6f}")

            if verbose:
                # Add test-specific details when in verbose mode
                for key, value in result.items():
                    if key not in ["name", "success", "p_value", "p_value1", "p_value2",
                                  "p_value_forward", "p_value_backward", "error"]:
                        if isinstance(value, float):
                            summary.append(f"  {key}: {value:.6f}")
                        elif isinstance(value, list) and len(value) > 10:
                            summary.append(f"  {key}: [...]")
                        else:
                            summary.append(f"  {key}: {value}")

            if "error" in result:
                summary.append(f"  Error: {result['error']}")

            summary.append("")

        return "\n".join(summary)
