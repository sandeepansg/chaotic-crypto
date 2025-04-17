"""
Pattern-based NIST statistical tests.
Implements Runs Test and Longest Run of Ones Test.
"""
import math
import scipy.special as spc
from typing import Dict, List, Any


class PatternTests:
    """
    Implementation of pattern-based statistical tests from NIST SP 800-22.
    """
    
    @staticmethod
    def runs_test(bits: List[int], significance_level: float = 0.01) -> Dict[str, Any]:
        """
        Runs Test - tests oscillation between zeros and ones.

        Args:
            bits: Binary sequence as list of bits
            significance_level: Alpha threshold for P-value

        Returns:
            dict: Test results including P-value and success status
        """
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
        # The NIST SP 800-22 prerequisite check
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
    def longest_run_ones_test(bits: List[int], significance_level: float = 0.01) -> Dict[str, Any]:
        """
        Longest Run of Ones Test - tests the length of the longest run of ones.

        Args:
            bits: Binary sequence as list of bits
            significance_level: Alpha threshold for P-value

        Returns:
            dict: Test results including P-value and success status
        """
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
            # Expected probabilities for each category
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
