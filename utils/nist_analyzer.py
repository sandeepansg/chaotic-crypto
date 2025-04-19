"""
NIST statistical test analyzer for chaotic systems.
Evaluates the randomness quality of sequences produced by the hyperchaotic system.
"""
from chaos.attractor import HyperchaosSystem
from utils.nist_core import NISTTestSuite
from utils.random_gen import SecureRandom


class NISTAnalyzer:
    """Analyzes chaotic sequences using NIST Statistical Tests."""
    
    @staticmethod
    def analyze_system(initial_state=None, sequence_size=100000, skip=1000, entropy=None, run_all_tests=False):
        """
        Analyze the hyperchaotic system using NIST tests.
        
        Args:
            initial_state: Initial values for the chaotic system [x, y, w, u, v]
            sequence_size: Size of sequence to generate for testing
            skip: Number of initial points to skip (transient)
            entropy: Optional user-provided entropy string
            run_all_tests: Force all tests to run regardless of sequence size
            
        Returns:
            dict: Analysis results
        """
        # Use entropy to generate initial state if provided
        if entropy and initial_state is None:
            initial_state = SecureRandom.generate_initial_state(entropy)
        # Use default initial state if none provided
        elif initial_state is None:
            initial_state = [0.1, 0.2, 0.3, 0.4, 0.5]
            
        # Create hyperchaotic system
        system = HyperchaosSystem()
        
        # Generate random sequence
        sequence = system.generate_bytes(initial_state, sequence_size, skip)
        
        # Run NIST tests
        results = NISTTestSuite.test_randomness(sequence, run_all_tests=run_all_tests)
        
        return {
            "system": "HyperchaosSystem",
            "sequence_size": sequence_size,
            "skip": skip,
            "initial_state": initial_state,
            "test_results": results
        }
    
    @staticmethod
    def analyze_sequence(sequence, run_all_tests=False):
        """
        Analyze an existing byte sequence using NIST tests.
        
        Args:
            sequence: Byte sequence to analyze
            run_all_tests: Force all tests to run regardless of sequence length
            
        Returns:
            dict: Analysis results
        """
        # Ensure sequence is bytes
        if not isinstance(sequence, (bytes, bytearray)):
            try:
                sequence = bytes(sequence)
            except (TypeError, ValueError):
                raise TypeError("sequence must be convertible to bytes")
    
        # Run NIST tests
        results = NISTTestSuite.test_randomness(sequence, run_all_tests=run_all_tests)
        
        return {
            "sequence_size": len(sequence),
            "test_results": results
        }

    @staticmethod
    def analyze_ciphertext(ciphertext, sample_size=None, run_all_tests=False):
        """
        Analyze ciphertext data using NIST tests.

        Args:
            ciphertext: Encrypted data bytes
            sample_size: Number of bytes to use for testing (None = use all)
            run_all_tests: Force all tests to run regardless of sequence length

        Returns:
            dict: Analysis results
        """
        # Ensure we have bytes to test
        if not isinstance(ciphertext, (bytes, bytearray)):
            raise TypeError("ciphertext must be bytes or bytearray")

        # If sample_size is specified, use only a portion of the ciphertext
        if sample_size and sample_size < len(ciphertext):
            # Skip the IV (first block_size bytes) when sampling
            # Assume block_size is 8 (default in the system)
            block_size = 8
            start_pos = block_size

            # If ciphertext is too small, use what's available
            if len(ciphertext) <= start_pos:
                sequence = ciphertext
            else:
                max_sample = len(ciphertext) - start_pos
                actual_sample = min(sample_size, max_sample)
                sequence = ciphertext[start_pos:start_pos + actual_sample]
        else:
            # Use the entire ciphertext except IV
            block_size = 8
            sequence = ciphertext[block_size:] if len(ciphertext) > block_size else ciphertext

        # Run NIST tests
        results = NISTTestSuite.test_randomness(sequence, run_all_tests=run_all_tests)

        return {
            "sequence_size": len(sequence),
            "sample_size": len(sequence),
            "original_size": len(ciphertext),
            "test_results": results
        }
        
    @staticmethod
    def analyze_with_specific_tests(binary_data, tests=None, significance_level=0.01):
        """
        Analyze data with specific NIST tests.
        
        Args:
            binary_data: Binary sequence as bytes, bytearray, or list of bits
            tests: List of test names to run (None = run all applicable tests)
            significance_level: Alpha threshold for P-values
            
        Returns:
            dict: Analysis results
        """
        # Ensure data is bytes
        if not isinstance(binary_data, (bytes, bytearray)):
            try:
                binary_data = bytes(binary_data)
            except (TypeError, ValueError):
                raise TypeError("binary_data must be convertible to bytes")
                
        # Prepare data
        bits = NISTTestSuite.prepare_data(binary_data)
        bits_length = len(bits)
        
        # Calculate optimal parameters
        params = NISTTestSuite.calculate_optimal_parameters(bits_length)
        
        # Determine applicable tests
        applicable_tests = NISTTestSuite.determine_test_applicability(bits_length)
        
        # Filter tests if specified
        results = {}
        if tests is None:
            # Run all applicable tests
            return NISTTestSuite.test_randomness(binary_data, significance_level)
        else:
            # Run only specified tests
            for test_name in tests:
                if test_name not in applicable_tests:
                    results[test_name] = {
                        "name": test_name,
                        "p_value": 0.0,
                        "success": False,
                        "error": f"Unknown test: {test_name}"
                    }
                    continue
                    
                if not applicable_tests[test_name]:
                    results[test_name] = {
                        "name": test_name,
                        "p_value": 0.0,
                        "success": False,
                        "error": f"Insufficient data for {test_name} test"
                    }
                    continue
                    
                # Run the specific test
                if test_name == "monobit":
                    results[test_name] = FrequencyTests.monobit_test(bits, significance_level)
                elif test_name == "block_frequency":
                    results[test_name] = FrequencyTests.block_frequency_test(
                        bits, block_size=params["block_freq_size"], significance_level=significance_level
                    )
                elif test_name == "runs":
                    results[test_name] = PatternTests.runs_test(bits, significance_level)
                elif test_name == "longest_run":
                    results[test_name] = PatternTests.longest_run_ones_test(bits, significance_level)
                elif test_name == "dft":
                    results[test_name] = SpectralTests.dft_test(bits, significance_level)
                elif test_name == "serial":
                    results[test_name] = EntropyTests.serial_test(
                        bits, block_size=params["serial_block_size"], significance_level=significance_level
                    )
                elif test_name == "approximate_entropy":
                    results[test_name] = EntropyTests.approximate_entropy_test(
                        bits, block_size=params["approx_block_size"], significance_level=significance_level
                    )
                elif test_name == "cumulative_sums":
                    results[test_name] = EntropyTests.cumulative_sums_test(bits, significance_level)
                elif test_name == "linear_complexity":
                    results[test_name] = ComplexityTests.linear_complexity_test(
                        bits, block_size=params["linear_complexity_size"], significance_level=significance_level
                    )
                elif test_name == "universal":
                    results[test_name] = ComplexityTests.universal_test(
                        bits, block_size=7, significance_level=significance_level
                    )
                elif test_name == "binary_matrix_rank":
                    results[test_name] = MatrixTests.binary_matrix_rank_test(bits, significance_level)
                elif test_name == "random_excursions":
                    results[test_name] = RandomExcursionsTests.random_excursions_test(bits, significance_level)
                elif test_name == "random_excursions_variant":
                    results[test_name] = RandomExcursionsTests.random_excursions_variant_test(bits, significance_level)
                elif test_name == "non_overlapping_template":
                    results[test_name] = TemplateTests.non_overlapping_template_test(
                        bits, block_size=params["template_block_size"], significance_level=significance_level
                    )
                elif test_name == "overlapping_template":
                    results[test_name] = TemplateTests.overlapping_template_test(bits, significance_level)
                    
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
