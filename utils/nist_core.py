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
from .nist_complexity_tests import ComplexityTests
from .nist_matrix_tests import MatrixTests
from .nist_random_excursions_tests import RandomExcursionsTests
from .nist_template_tests import TemplateTests


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
        
        # Linear complexity block size
        linear_complexity_size = min(5000, max(500, bits_length // 200))
        
        # Template test block size for non-overlapping test
        template_block_size = min(8192, max(1024, bits_length // 100))
        
        return {
            "serial_block_size": serial_block_size,
            "approx_block_size": approx_block_size,
            "block_freq_size": block_freq_size,
            "linear_complexity_size": linear_complexity_size,
            "template_block_size": template_block_size
        }

    @staticmethod
    def determine_test_applicability(bits_length: int) -> Dict[str, bool]:
        """Determine which tests can be applied based on sequence length."""
        result = {
            "monobit": True,
            "block_frequency": bits_length >= 100,
            "runs": True,
            "longest_run": bits_length >= 128,
            "dft": bits_length >= 1000,
            "serial": bits_length >= 16,
            "approximate_entropy": bits_length >= 100,
            "cumulative_sums": True,
            "linear_complexity": bits_length >= 1000000,
            "universal": bits_length >= 387840,  # Minimum for block size 6
            "binary_matrix_rank": bits_length >= 38*32*32,  # Minimum for 38 matrices
            "random_excursions": bits_length >= 1000000,
            "random_excursions_variant": bits_length >= 1000000,
            "non_overlapping_template": bits_length >= 1024,
            "overlapping_template": bits_length >= 1032
        }
        return result
    
    @staticmethod
    def test_randomness(binary_data: Union[bytes, bytearray, List[int]], 
                        significance_level: float = 0.01,
                        run_all_tests: bool = False) -> Dict[str, Any]:
        """
        Run all available statistical tests on a binary sequence.

        Args:
            binary_data: Binary sequence as bytes, bytearray, or list of bits
            significance_level: Alpha threshold for P-values
            run_all_tests: Force all tests to run even if data length is insufficient

        Returns:
            dict: Results of all tests
        """
        results = {}
        
        # Prepare data
        bits = NISTTestSuite.prepare_data(binary_data)
        bits_length = len(bits)
        
        # Calculate optimal parameters
        params = NISTTestSuite.calculate_optimal_parameters(bits_length)
        
        # Determine which tests can be applied
        applicable_tests = NISTTestSuite.determine_test_applicability(bits_length)
        if run_all_tests:
            # Force all tests to run
            applicable_tests = {k: True for k in applicable_tests}

        # Run frequency tests
        if applicable_tests["monobit"]:
            results["monobit"] = FrequencyTests.monobit_test(bits, significance_level)
        
        if applicable_tests["block_frequency"]:
            results["block_frequency"] = FrequencyTests.block_frequency_test(
                bits, 
                block_size=params["block_freq_size"], 
                significance_level=significance_level
            )
        
        # Run pattern tests
        if applicable_tests["runs"]:
            results["runs"] = PatternTests.runs_test(bits, significance_level)
        
        if applicable_tests["longest_run"]:
            results["longest_run"] = PatternTests.longest_run_ones_test(bits, significance_level)
        
        # Run spectral tests
        if applicable_tests["dft"]:
            results["dft"] = SpectralTests.dft_test(bits, significance_level)
        
        # Run entropy tests
        if applicable_tests["serial"]:
            results["serial"] = EntropyTests.serial_test(
                bits, 
                block_size=params["serial_block_size"], 
                significance_level=significance_level
            )
        
        if applicable_tests["approximate_entropy"]:
            results["approximate_entropy"] = EntropyTests.approximate_entropy_test(
                bits, 
                block_size=params["approx_block_size"], 
                significance_level=significance_level
            )
        
        if applicable_tests["cumulative_sums"]:
            results["cumulative_sums"] = EntropyTests.cumulative_sums_test(bits, significance_level)
        
        # Run complexity tests
        if applicable_tests["linear_complexity"]:
            results["linear_complexity"] = ComplexityTests.linear_complexity_test(
                bits,
                block_size=params["linear_complexity_size"],
                significance_level=significance_level
            )
        
        if applicable_tests["universal"]:
            results["universal"] = ComplexityTests.universal_test(
                bits,
                block_size=7,  # Default recommended value
                significance_level=significance_level
            )
        
        # Run matrix tests
        if applicable_tests["binary_matrix_rank"]:
            results["binary_matrix_rank"] = MatrixTests.binary_matrix_rank_test(
                bits,
                significance_level=significance_level
            )
        
        # Run random excursions tests
        if applicable_tests["random_excursions"]:
            results["random_excursions"] = RandomExcursionsTests.random_excursions_test(
                bits, 
                significance_level=significance_level
            )
        
        if applicable_tests["random_excursions_variant"]:
            results["random_excursions_variant"] = RandomExcursionsTests.random_excursions_variant_test(
                bits, 
                significance_level=significance_level
            )
        
        # Run template tests
        if applicable_tests["non_overlapping_template"]:
            results["non_overlapping_template"] = TemplateTests.non_overlapping_template_test(
                bits,
                m=9,  # Default template length
                block_size=params["template_block_size"],
                significance_level=significance_level
            )
        
        if applicable_tests["overlapping_template"]:
            results["overlapping_template"] = TemplateTests.overlapping_template_test(
                bits,
                m=9,  # Default template length
                significance_level=significance_level
            )

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
