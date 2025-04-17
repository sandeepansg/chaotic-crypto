"""
Core functionality for NIST statistical test suite.
Provides common utilities and the main API for randomness testing.
"""
import math
import numpy as np
from typing import Dict, List, Union, Any

# Import individual test modules
from .nist_freq_tests import FrequencyTests
from .nist_pattern_tests import PatternTests
from .nist_spectral_tests import SpectralTests
from .nist_entropy_tests import EntropyTests


class NISTTestSuite:
    """
    Main API for NIST statistical tests.
    Provides a clean interface for running randomness tests.
    """
    
    @staticmethod
    def bytes_to_bits(data: bytes) -> List[int]:
        """Convert bytes to a list of bits in correct order (MSB to LSB)."""
        bits = []
        for byte in data:
            for i in range(7, -1, -1):  # MSB to LSB (7 to 0)
                bits.append((byte >> i) & 1)
        return bits
    
    @staticmethod
    def prepare_data(binary_data: Union[bytes, bytearray, List[int]]) -> List[int]:
        """Ensure data is in the correct format (list of bits)."""
        if isinstance(binary_data, (bytes, bytearray)):
            return NISTTestSuite.bytes_to_bits(binary_data)
        else:
            return binary_data

    @staticmethod
    def calculate_optimal_parameters(bits_length: int) -> Dict[str, Any]:
        """Calculate optimal test parameters based on sequence length."""
        # Serial test block size
        serial_block_size = min(16, int(math.log2(bits_length)) - 2)
        serial_block_size = max(serial_block_size, 3)  # Ensure at least 3 for delta2
        
        # Approximate entropy block size
        approx_block_size = min(10, int(math.log2(bits_length)) - 5)
        approx_block_size = max(approx_block_size, 2)  # Ensure at least 2
        
        # Block frequency test block size
        block_freq_size = min(128, max(20, bits_length // 100))
        
        return {
            "serial_block_size": serial_block_size,
            "approx_block_size": approx_block_size,
            "block_freq_size": block_freq_size
        }
    
    @staticmethod
    def test_randomness(binary_data: Union[bytes, bytearray, List[int]], 
                        significance_level: float = 0.01) -> Dict[str, Any]:
        """
        Run all available statistical tests on a binary sequence.

        Args:
            binary_data: Binary sequence as bytes, bytearray, or list of bits
            significance_level: Alpha threshold for P-values

        Returns:
            dict: Results of all tests
        """
        results = {}
        
        # Prepare data
        bits = NISTTestSuite.prepare_data(binary_data)
        bits_length = len(bits)
        
        # Calculate optimal parameters
        params = NISTTestSuite.calculate_optimal_parameters(bits_length)

        # Run frequency tests
        results["monobit"] = FrequencyTests.monobit_test(bits, significance_level)
        results["block_frequency"] = FrequencyTests.block_frequency_test(
            bits, 
            block_size=params["block_freq_size"], 
            significance_level=significance_level
        )
        
        # Run pattern tests
        results["runs"] = PatternTests.runs_test(bits, significance_level)
        results["longest_run"] = PatternTests.longest_run_ones_test(bits, significance_level)
        
        # Run spectral tests
        results["dft"] = SpectralTests.dft_test(bits, significance_level)
        
        # Run entropy tests
        results["serial"] = EntropyTests.serial_test(
            bits, 
            block_size=params["serial_block_size"], 
            significance_level=significance_level
        )
        
        results["approximate_entropy"] = EntropyTests.approximate_entropy_test(
            bits, 
            block_size=params["approx_block_size"], 
            significance_level=significance_level
        )
        
        results["cumulative_sums"] = EntropyTests.cumulative_sums_test(bits, significance_level)

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
