"""
Frequency-based NIST statistical tests.
Implements Monobit Test and Block Frequency Test.
"""
import math
import scipy.special as spc
from typing import Dict, List, Any


class FrequencyTests:
    """
    Implementation of frequency-based statistical tests from NIST SP 800-22
    """
    
    @staticmethod
    def monobit_test(bits: List[int], significance_level: float = 0.01) -> Dict[str, Any]:
        """
        Frequency (Monobit) Test - tests the proportion of zeros and ones.
        
        Args:
            bits: Binary sequence as list of bits
            significance_level: Alpha threshold for P-value
            
        Returns:
            dict: Test results including P-value and success status
        """
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
    def block_frequency_test(bits: List[int], block_size: int = 128, 
                             significance_level: float = 0.01) -> Dict[str, Any]:
        """
        Block Frequency Test - tests the proportion of ones in blocks.
        
        Args:
            bits: Binary sequence as list of bits
            block_size: Size of each block to analyze
            significance_level: Alpha threshold for P-value
            
        Returns:
            dict: Test results including P-value and success status
        """
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
