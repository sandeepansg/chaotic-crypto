"""
Complexity-based NIST statistical tests.
Implements Linear Complexity Test and Maurer's Universal Statistical Test.
"""
import math
import numpy as np
import scipy.special as spc
from typing import Dict, List, Any


class ComplexityTests:
    """
    Implementation of complexity-based statistical tests from NIST SP 800-22.
    """
    
    @staticmethod
    def _berlekamp_massey(sequence):
        """
        Berlekamp-Massey algorithm to compute linear complexity.
        
        Args:
            sequence: Binary sequence as list of bits
            
        Returns:
            int: Linear complexity of the sequence
        """
        n = len(sequence)
        c = np.zeros(n, dtype=int)
        b = np.zeros(n, dtype=int)
        
        c[0] = 1
        b[0] = 1
        
        L = 0
        m = -1
        
        # Optimized implementation using NumPy operations when possible
        for N in range(n):
            # Compute discrepancy
            d = sequence[N]
            if L > 0:
                # Use vectorized operation for faster computation
                indices = np.arange(1, L + 1)
                products = c[indices] * np.array([sequence[N - i] for i in indices], dtype=int)
                d = (d + np.sum(products)) % 2
            
            if d == 1:  # Need to update LFSR
                t = c.copy()
                
                # Update connection polynomial
                if N - m + n > len(c):
                    c = np.pad(c, (0, N - m + n - len(c)), 'constant')
                    b = np.pad(b, (0, N - m + n - len(b)), 'constant')
                
                for j in range(n - N + m):
                    if j < len(b):
                        c[N - m + j] = (c[N - m + j] + b[j]) % 2
                
                if L <= N / 2:
                    L = N + 1 - L
                    m = N
                    b = t
        
        return L
    
    @staticmethod
    def linear_complexity_test(bits: List[int], block_size: int = 500, 
                           significance_level: float = 0.01) -> Dict[str, Any]:
        """
        Linear Complexity Test - tests complexity of a sequence against expectation
        for a random sequence.
        
        Args:
            bits: Binary sequence as list of bits
            block_size: Size of blocks for analysis
            significance_level: Alpha threshold for P-value
            
        Returns:
            dict: Test results including P-value and success status
        """
        n = len(bits)
        
        # Check parameters
        if block_size < 500 or block_size > 5000:
            return {
                "name": "Linear Complexity Test",
                "p_value": 0.0,
                "success": False,
                "error": f"Block size should be between 500 and 5000 (got {block_size})"
            }
            
        # Number of blocks
        N = n // block_size
        
        if N < 4:
            return {
                "name": "Linear Complexity Test",
                "p_value": 0.0,
                "success": False,
                "error": f"Insufficient blocks: need at least 4, got {N} (sequence length: {n})"
            }
            
        # Expected mean for block of size M
        # For large block_size, use simplified approximation
        mu = 0.5 * block_size + 1/36
        
        # Initialize frequency counts for each K value
        K = 6  # Number of chi-square categories -1
        v = np.zeros(K + 1)
        
        # Process each block
        complexities = []  # Store for detailed reporting
        for i in range(N):
            # Extract current block
            block = bits[i * block_size:(i + 1) * block_size]
            
            # Compute linear complexity
            complexity = ComplexityTests._berlekamp_massey(block)
            complexities.append(complexity)
            
            # Calculate Ti value (mean-adjusted complexity)
            T = (-1)**block_size * (complexity - mu) + 2/9
            
            # Assign to appropriate category (folded into K+1 bins)
            if T <= -2.5:
                v[0] += 1
            elif T <= -1.5:
                v[1] += 1
            elif T <= -0.5:
                v[2] += 1
            elif T <= 0.5:
                v[3] += 1
            elif T <= 1.5:
                v[4] += 1
            elif T <= 2.5:
                v[5] += 1
            else:
                v[6] += 1
        
        # Expected probabilities for each category
        pi = [0.010417, 0.031250, 0.125000, 0.500000, 0.250000, 0.062500, 0.020833]
        
        # Calculate chi-squared
        chi_squared = 0
        for i in range(K + 1):
            expected = N * pi[i]
            chi_squared += ((v[i] - expected)**2) / expected
        
        # Calculate P-value with K degrees of freedom
        p_value = spc.gammaincc(K/2, chi_squared/2)
        
        # Compute statistics for detailed report
        avg_complexity = np.mean(complexities)
        min_complexity = np.min(complexities)
        max_complexity = np.max(complexities)
        
        return {
            "name": "Linear Complexity Test",
            "p_value": p_value,
            "success": p_value >= significance_level,
            "chi_squared": chi_squared,
            "block_size": block_size,
            "num_blocks": N,
            "expected_mean": mu,
            "observed_frequencies": v.tolist(),
            "avg_complexity": avg_complexity,
            "min_complexity": min_complexity,
            "max_complexity": max_complexity
        }
        
    @staticmethod
    def universal_test(bits: List[int], block_size: int = 7, significance_level: float = 0.01) -> Dict[str, Any]:
        """
        Maurer's Universal Statistical Test - test for compressibility.
        
        Args:
            bits: Binary sequence as list of bits
            block_size: Length of each template block (L)
            significance_level: Alpha threshold for P-value
            
        Returns:
            dict: Test results including P-value and success status
        """
        n = len(bits)
        
        # Check block size (L)
        if block_size < 2 or block_size > 16:
            return {
                "name": "Universal Statistical Test",
                "p_value": 0.0,
                "success": False,
                "error": f"Block size L must be between 2 and 16 (got {block_size})"
            }
        
        # Initialize parameters based on block size
        # Expected values (theoretical) for specified block sizes
        expected_value = {
            1: 0.7326495, 2: 1.5374383, 3: 2.4016068, 4: 3.3112247, 5: 4.2534266,
            6: 5.2177052, 7: 6.1962507, 8: 7.1836656, 9: 8.1764248, 10: 9.1723243,
            11: 10.170032, 12: 11.168765, 13: 12.168070, 14: 13.167693, 15: 14.167488,
            16: 15.167379
        }
        
        variance = {
            1: 0.690, 2: 1.338, 3: 1.901, 4: 2.358, 5: 2.705, 6: 2.954, 7: 3.125,
            8: 3.238, 9: 3.311, 10: 3.356, 11: 3.384, 12: 3.401, 13: 3.410,
            14: 3.416, 15: 3.419, 16: 3.421
        }
        
        # K is initialization segment - default to 10*2^L
        K = 10 * (2**block_size)
                
        # Check if there's enough data
        # Total blocks needed is K + Q where Q is test segment
        # Following NIST recommendations, Q should be at least 1000 * 2^L
        Q = 1000 * (2**block_size)
        
        total_blocks_needed = K + Q
        if n < total_blocks_needed * block_size:
            return {
                "name": "Universal Statistical Test",
                "p_value": 0.0,
                "success": False,
                "error": f"Insufficient data: need at least {total_blocks_needed * block_size} bits, got {n}"
            }
        
        # Initialize dictionary for last occurrence of each pattern
        pattern_dict = {}
        
        # Variables for calculating test statistic
        sum_value = 0.0
        sum_squared = 0.0  # For variance calculation
        all_distances = []  # Store distances for detailed reporting
        
        # First K blocks are for initialization
        for i in range(K):
            # Extract pattern from block
            block_start = i * block_size
            # Use bit shifting for pattern extraction (more efficient)
            pattern = 0
            for j in range(block_size):
                pattern = (pattern << 1) | bits[block_start + j]
            
            # Store position of pattern
            pattern_dict[pattern] = i + 1
        
        # Process the test blocks
        for i in range(K, K + Q):
            # Extract pattern from block
            block_start = i * block_size
            pattern = 0
            for j in range(block_size):
                pattern = (pattern << 1) | bits[block_start + j]
            
            # Calculate distance to last occurrence
            distance = i + 1 - pattern_dict.get(pattern, 0)
            
            # Add log2 of the distance to sum if pattern has occurred before
            if distance > 0:
                log_dist = math.log2(distance)
                sum_value += log_dist
                sum_squared += log_dist ** 2
                all_distances.append(distance)
            
            # Update last occurrence
            pattern_dict[pattern] = i + 1
        
        # Calculate test statistic
        fn_value = sum_value / Q
        
        # Calculate observed variance
        observed_variance = sum_squared/Q - (fn_value**2)
        
        # Standardize the test statistic
        sigma = math.sqrt(variance[block_size] / Q) * 0.7  # Conservative factor
        
        # Calculate the standardized test statistic
        c = 0.7  # Correction factor for improved approximation
        expected = expected_value[block_size]
        standardized_value = c * abs(fn_value - expected) / sigma
        
        # Calculate P-value
        p_value = math.erfc(standardized_value / math.sqrt(2))
        
        # Additional statistics for detailed reporting
        distance_stats = {
            "min": min(all_distances) if all_distances else 0,
            "max": max(all_distances) if all_distances else 0,
            "mean": sum(all_distances)/len(all_distances) if all_distances else 0
        }
        
        return {
            "name": "Universal Statistical Test",
            "p_value": p_value,
            "success": p_value >= significance_level,
            "fn_value": fn_value,
            "expected_value": expected,
            "block_size": block_size,
            "init_blocks": K,
            "test_blocks": Q,
            "standardized_value": standardized_value,
            "observed_variance": observed_variance,
            "expected_variance": variance[block_size],
            "distance_stats": distance_stats
        }
