"""
Entropy-based NIST statistical tests.
Implements Serial Test, Approximate Entropy Test, and Cumulative Sums Test.
"""
import math
import numpy as np
import scipy.special as spc
from typing import Dict, List, Any


class EntropyTests:
    """
    Implementation of entropy-based statistical tests from NIST SP 800-22.
    """
    
    @staticmethod
    def serial_test(bits: List[int], block_size: int = 16, 
                    significance_level: float = 0.01) -> Dict[str, Any]:
        """
        Serial Test - tests uniformity of patterns of given length.

        Args:
            bits: Binary sequence as list of bits
            block_size: Size of patterns to test (m value)
            significance_level: Alpha threshold for P-value

        Returns:
            dict: Test results including P-values and success status
        """
        n = len(bits)

        # Block size validation
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
    def approximate_entropy_test(bits: List[int], block_size: int = 10, 
                                significance_level: float = 0.01) -> Dict[str, Any]:
        """
        Approximate Entropy Test - compares frequencies of overlapping patterns.

        Args:
            bits: Binary sequence as list of bits
            block_size: Size of blocks for comparison (m value)
            significance_level: Alpha threshold for P-value

        Returns:
            dict: Test results including P-value and success status
        """
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
    def cumulative_sums_test(bits: List[int], significance_level: float = 0.01) -> Dict[str, Any]:
        """
        Cumulative Sums Test - tests if cumulative sum of partial sequences is too large or too small.

        Args:
            bits: Binary sequence as list of bits
            significance_level: Alpha threshold for P-value

        Returns:
            dict: Test results including P-values and success status
        """
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
