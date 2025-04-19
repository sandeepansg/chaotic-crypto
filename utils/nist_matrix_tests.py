"""
Matrix-based NIST statistical tests.
Implements Binary Matrix Rank Test.
"""
import math
import numpy as np
from typing import Dict, List, Any


class MatrixTests:
    """
    Implementation of matrix-based statistical tests from NIST SP 800-22.
    """
    
    @staticmethod
    def _compute_rank(matrix):
        """Compute the rank of a binary matrix using Gaussian elimination."""
        # Working on a copy to avoid modifying the original
        m = matrix.copy()
        n_rows, n_cols = m.shape
        
        # Current rank
        rank = 0
        
        # For each row
        for row in range(min(n_rows, n_cols)):
            # Find pivot
            pivot_found = False
            for i in range(row, n_rows):
                if m[i, row] == 1:
                    # Swap rows
                    if i != row:
                        m[[row, i]] = m[[i, row]]
                    pivot_found = True
                    break
            
            if not pivot_found:
                # No pivot in this column, move to next column
                continue
                
            # Eliminate below
            for i in range(row + 1, n_rows):
                if m[i, row] == 1:
                    m[i] = np.bitwise_xor(m[i], m[row])
            
            # Increment rank
            rank += 1
            
        return rank
    
    @staticmethod
    def binary_matrix_rank_test(bits: List[int], significance_level: float = 0.01) -> Dict[str, Any]:
        """
        Binary Matrix Rank Test - tests linear dependence among fixed-length 
        substrings of the original sequence.
        
        Args:
            bits: Binary sequence as list of bits
            significance_level: Alpha threshold for P-value
            
        Returns:
            dict: Test results including P-value and success status
        """
        n = len(bits)
        
        # NIST recommended parameters
        # Matrix dimensions - use 32x32 for sequences >= 10^6 bits
        if n >= 1000000:
            M = 32
            Q = 32
        else:
            M = 32  # Number of rows
            Q = 32  # Number of columns
        
        # Check that there's enough data for at least 38 matrices
        # (NIST recommendation for stability of the chi-square test)
        if n < 38 * M * Q:
            return {
                "name": "Binary Matrix Rank Test",
                "p_value": 0.0,
                "success": False,
                "error": f"Insufficient data length: need at least {38 * M * Q} bits"
            }
            
        # Number of matrices that can be constructed
        N = n // (M * Q)
        
        # Initialize counters for ranks
        F_M = 0  # Full rank
        F_M1 = 0  # Full rank - 1
        F_other = 0  # Other ranks
        
        # Process each matrix
        for k in range(N):
            start = k * M * Q
            matrix_bits = bits[start:start + M * Q]
            
            # Reshape bits into MxQ matrix
            matrix = np.array(matrix_bits).reshape(M, Q)
            
            # Compute rank
            rank = MatrixTests._compute_rank(matrix)
            
            # Update counters
            if rank == M:  # Full rank (assuming M <= Q)
                F_M += 1
            elif rank == M - 1:  # Full rank - 1
                F_M1 += 1
            else:  # Other ranks
                F_other += 1
                
        # Expected probabilities based on asymptotic analysis by NIST
        # Probability of rank = M (full rank)
        p_M = np.prod([1.0 - 2**(i-Q) for i in range(1, M+1)])
        
        # Probability of rank = M-1
        p_M1 = np.prod([1.0 - 2**(i-Q) for i in range(1, M)]) * \
               (1.0 - np.prod([1.0 - 2**(i-M) for i in range(1, Q+1)]))
        
        # Probability of other ranks
        p_other = 1.0 - p_M - p_M1
        
        # Expected counts
        E_M = N * p_M
        E_M1 = N * p_M1
        E_other = N * p_other
        
        # Chi-square computation (with Yates' correction)
        chi_squared = ((F_M - E_M)**2 / E_M + 
                      (F_M1 - E_M1)**2 / E_M1 + 
                      (F_other - E_other)**2 / E_other)
        
        # Degrees of freedom for chi-square test is 2
        p_value = math.exp(-chi_squared / 2.0)
        
        return {
            "name": "Binary Matrix Rank Test",
            "p_value": p_value,
            "success": p_value >= significance_level,
            "chi_squared": chi_squared,
            "matrices": N,
            "full_rank": F_M,
            "full_rank_minus_1": F_M1,
            "other_ranks": F_other,
            "matrix_size": f"{M}x{Q}"
        }
