"""
Spectral-based NIST statistical tests.
Implements Discrete Fourier Transform Test.
"""
import math
import numpy as np
from typing import Dict, List, Any


class SpectralTests:
    """
    Implementation of spectral-based statistical tests from NIST SP 800-22.
    """
    
    @staticmethod
    def dft_test(bits: List[int], significance_level: float = 0.01) -> Dict[str, Any]:
        """
        Discrete Fourier Transform Test - detects periodic features.

        Args:
            bits: Binary sequence as list of bits
            significance_level: Alpha threshold for P-value

        Returns:
            dict: Test results including P-value and success status
        """
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
