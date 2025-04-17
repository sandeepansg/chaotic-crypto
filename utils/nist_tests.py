"""
NIST statistical test suite for evaluating cryptographic randomness.
Implementation of key tests from NIST SP 800-22 with fixes.
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
    def bytes_to_bits(data):
        """Convert bytes to a list of bits in correct order (MSB to LSB)."""
        bits = []
        for byte in data:
            for i in range(7, -1, -1):  # MSB to LSB (7 to 0)
                bits.append((byte >> i) & 1)
        return bits
    
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
        # Convert to bits if needed
        if isinstance(binary_data, (bytes, bytearray)):
            bits = NISTTests.bytes_to_bits(binary_data)
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
            bits = NISTTests.bytes_to_bits(binary_data)
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
            bits = NISTTests.bytes_to_bits(binary_data)
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
        # The correct prerequisite check according to NIST SP 800-22
        tau = 2 / math.sqrt(n)
        if abs(pi - 0.5) >= tau:
            return {
                "name": "Runs Test",
                "p_value": 0.0,
                "success": False,
                "error": f"Prerequisite monobit test failed: |{pi:.6f}-0.5|={abs(pi-0.5):.6f} >= {tau:.6f}"
            }

        # Count runs
        runs = 1
        for i in range(1, n):
            if bits[i] != bits[i-1]:
                runs += 1

        # Calculate expected runs
        exp_runs = 2 * n * pi * (1 - pi)
        
        # Calculate test statistic
        # Corrected formula per NIST documentation
        std_dev = math.sqrt(2 * n * pi * (1 - pi))
        v_obs = (runs - exp_runs) / std_dev

        # Calculate P-value
        p_value = math.erfc(abs(v_obs) / math.sqrt(2))

        return {
            "name": "Runs Test",
            "p_value": p_value,
            "success": p_value >= significance_level,
            "runs": runs,
            "expected_runs": exp_runs,
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
            bits = NISTTests.bytes_to_bits(binary_data)
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
            K = 3  # Number of degrees of freedom (categories-1)
            # Expected probabilities for each category (correct per NIST docs)
            pi = [0.2148, 0.3672, 0.2305, 0.1875]
            # Category boundaries
            v_categories = [0, 1, 2, 3]  # <= 1, 2, 3, >= 4
        elif n < 750000:
            M = 128
            K = 5
            pi = [0.1174, 0.2430, 0.2493, 0.1752, 0.1027, 0.1124]
            v_categories = [0, 1, 2, 3, 4, 5]  # <= 1, 2-3, 4, 5, 6-7, >= 8
        else:
            M = 10000
            K = 6
            pi = [0.0882, 0.2092, 0.2483, 0.1933, 0.1208, 0.0675, 0.0727]
            v_categories = [0, 1, 2, 3, 4, 5, 6]  # <= 1, 2-3, 4-6, 7-10, 11-15, 16-22, >= 23

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

            # Categorize the longest run based on length and sequence size
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
                elif longest in (2, 3):
                    v[1] += 1
                elif longest == 4:
                    v[2] += 1
                elif longest == 5:
                    v[3] += 1
                elif longest in (6, 7):
                    v[4] += 1
                else:  # longest >= 8
                    v[5] += 1
            else:  # For long sequences - corrected categories
                if longest <= 1:
                    v[0] += 1
                elif longest in (2, 3):
                    v[1] += 1
                elif longest in (4, 5, 6):
                    v[2] += 1
                elif 7 <= longest <= 10:
                    v[3] += 1
                elif 11 <= longest <= 15:
                    v[4] += 1
                elif 16 <= longest <= 22:
                    v[5] += 1
                else:  # longest >= 23
                    v[6] += 1

        # Calculate chi-squared
        chi_squared = sum((v[i] - N * pi[i])**2 / (N * pi[i]) for i in range(len(pi)))

        # Calculate P-value with correct degrees of freedom
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
            bits = NISTTests.bytes_to_bits(binary_data)
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
        modulus = np.abs(S[1:n//2 + 1])  # Skip DC component (S[0])

        # Calculate threshold - corrected formula
        T = math.sqrt(math.log(1/0.05) * n)

        # Count values below threshold
        N0 = 0.95 * n / 2  # Expected count
        N1 = sum(1 for m in modulus if m < T)  # Observed count

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
            bits = NISTTests.bytes_to_bits(binary_data)
        else:
            bits = binary_data

        n = len(bits)

        # Block size validation - fixed prerequisite check
        if block_size < 2 or block_size > int(math.log2(n)) - 2:
            return {
                "name": "Serial Test",
                "p_value1": 0.0,
                "p_value2": 0.0,
                "success": False,
                "error": f"Invalid block size {block_size} for sequence length {n}"
            }

        # Helper function to count patterns of a specific length
        def psi_sq_m(m):
            # Create dictionary for pattern counts
            pattern_counts = {}
            
            # Count each pattern (with wrap-around)
            for i in range(n):
                pattern = 0
                for j in range(m):
                    pattern = (pattern << 1) | bits[(i + j) % n]
                # Count this pattern
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
                
            # Calculate and return psi-square statistic
            return 2**m / n * sum(count**2 for count in pattern_counts.values()) - n

        # Calculate psi-square statistics
        psisq_m = psi_sq_m(block_size)
        psisq_m1 = psi_sq_m(block_size - 1)
        psisq_m2 = psi_sq_m(block_size - 2) if block_size >= 3 else 0
        
        # Calculate deltas
        delta1 = psisq_m - psisq_m1
        delta2 = psisq_m - 2 * psisq_m1 + psisq_m2

        # Calculate P-values with correct degrees of freedom
        p_value1 = spc.gammaincc(2**(block_size-2), delta1/2)
        p_value2 = spc.gammaincc(2**(block_size-3), delta2/2) if block_size >= 3 else 1.0

        return {
            "name": "Serial Test",
            "p_value1": p_value1,
            "p_value2": p_value2,
            "success": p_value1 >= significance_level and p_value2 >= significance_level,
            "delta1": delta1,
            "delta2": delta2,
            "block_size": block_size
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
            bits = NISTTests.bytes_to_bits(binary_data)
        else:
            bits = binary_data

        n = len(bits)

        # Check for sufficient data and valid block size
        if n < 100 or block_size >= math.log2(n):
            return {
                "name": "Approximate Entropy Test",
                "p_value": 0.0,
                "success": False,
                "error": f"Insufficient data length or invalid block size {block_size}"
            }

        # Function to calculate phi values
        def phi(m):
            # Create and initialize C array
            c = [0] * (2**m)
            
            # Count pattern occurrences
            for i in range(n):
                # Extract pattern with wrap-around
                pattern = 0
                for j in range(m):
                    bit = bits[(i + j) % n]
                    pattern = (pattern << 1) | bit
                c[pattern] += 1
            
            # Convert counts to probabilities
            c = [x/n for x in c]
            
            # Calculate phi
            return sum(p * math.log(p) if p > 0 else 0 for p in c)

        # Calculate phi values
        phi_m = phi(block_size)
        phi_m1 = phi(block_size + 1)

        # Calculate ApEn
        apen = phi_m - phi_m1

        # Calculate chi-squared
        chi_sq = 2.0 * n * (math.log(2) - apen)

        # Calculate P-value with correct degrees of freedom
        p_value = spc.gammaincc(2**(block_size-1), chi_sq/2.0)

        return {
            "name": "Approximate Entropy Test",
            "p_value": p_value,
            "success": p_value >= significance_level,
            "chi_squared": chi_sq,
            "apen": apen,
            "block_size": block_size
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
            bits = NISTTests.bytes_to_bits(binary_data)
        else:
            bits = binary_data

        n = len(bits)

        # Check for sufficient data
        if n < 100:
            return {
                "name": "Cumulative Sums Test",
                "p_value_forward": 0.0,
                "p_value_backward": 0.0,
                "success": False,
                "error": "Insufficient data length"
            }

        # Convert to ±1
        x = [2 * bit - 1 for bit in bits]

        # Helper function to calculate P-value
        def calculate_p_value(z, n):
            # Limit k for computational efficiency
            k_max = min(int(math.floor(((n/z)-1)/4)), 100)
            k_start = -k_max if k_max > 0 else -1
            
            total = 0.0
            for k in range(k_start, k_max+1):
                total += math.erfc((4*k+1)*z/math.sqrt(2*n))
                total -= math.erfc((4*k-1)*z/math.sqrt(2*n))
                
            return total

        # Mode 0 (forward)
        S = np.cumsum(x)
        z_max = max(abs(S))

        # Calculate P-value for forward
        p_value_forward = 1.0 - calculate_p_value(z_max, n)

        # Mode 1 (backward)
        S_rev = np.cumsum(x[::-1])
        z_max_rev = max(abs(S_rev))

        # Calculate P-value for backward
        p_value_backward = 1.0 - calculate_p_value(z_max_rev, n)

        return {
            "name": "Cumulative Sums Test",
            "p_value_forward": p_value_forward,
            "p_value_backward": p_value_backward,
            "success": p_value_forward >= significance_level and p_value_backward >= significance_level,
            "z_forward": z_max,
            "z_backward": z_max_rev
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
        
        # Adjust block size for serial test based on sequence length
        if isinstance(binary_data, (bytes, bytearray)):
            bits_length = len(binary_data) * 8
        else:
            bits_length = len(binary_data)
            
        # Choose an appropriate block size based on sequence length
        serial_block_size = min(16, int(math.log2(bits_length)) - 2)
        serial_block_size = max(serial_block_size, 3)  # Ensure at least 3 for delta2
        
        results["serial"] = NISTTests.serial_test(binary_data, block_size=serial_block_size, significance_level=significance_level)
        
        # Choose block size for approximate entropy test
        approx_block_size = min(10, int(math.log2(bits_length)) - 5)
        approx_block_size = max(approx_block_size, 2)  # Ensure at least 2
        
        results["approximate_entropy"] = NISTTests.approximate_entropy_test(
            binary_data, block_size=approx_block_size, significance_level=significance_level)
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

            if "error" in result:
                summary.append(f"  Error: {result['error']}")

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

            summary.append("")

        return "\n".join(summary)
