"""Chebyshev polynomial implementation with modular arithmetic."""
import numpy as np
from functools import lru_cache


class ChebyshevPoly:
    """Handles Chebyshev polynomial calculations over modular arithmetic."""

    def __init__(self, modulus):
        self.mod = modulus

    def eval(self, degree, x):
        """Compute the nth Chebyshev polynomial at x (mod q)."""
        x %= self.mod
        
        # Base cases
        if degree == 0: return 1
        if degree == 1: return x
        
        # Use matrix exponentiation for large degrees
        if degree > 100:
            return self._matrix_eval(degree, x)
        
        # Use recursive relation for medium-sized degrees with caching
        return self._recursive_eval(degree, x)
    
    @lru_cache(maxsize=1024)
    def _recursive_eval(self, degree, x):
        """Compute Chebyshev polynomial using recursive relation with caching."""
        if degree == 0: return 1
        if degree == 1: return x
        
        t0, t1 = 1, x
        for _ in range(2, degree + 1):
            t_next = (2 * x * t1 - t0) % self.mod
            t0, t1 = t1, t_next
        return t1

    def _matrix_eval(self, degree, x):
        """Compute Chebyshev polynomial using matrix exponentiation."""
        matrix = np.array([[2 * x % self.mod, self.mod - 1], [1, 0]], dtype=object)
        result = self._matrix_pow(matrix, degree - 1)
        return (x * result[0, 0] + result[0, 1]) % self.mod

    def _matrix_pow(self, matrix, power):
        """Compute matrix^power using binary exponentiation."""
        result = np.array([[1, 0], [0, 1]], dtype=object)
        
        while power > 0:
            if power % 2 == 1:
                result = self._matrix_multiply(result, matrix)
            matrix = self._matrix_multiply(matrix, matrix)
            power //= 2
            
        return result

    def _matrix_multiply(self, a, b):
        """Multiply two 2x2 matrices with modular arithmetic."""
        result = np.zeros((2, 2), dtype=object)
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    result[i, j] = (result[i, j] + a[i, k] * b[k, j]) % self.mod
        return result
