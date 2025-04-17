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
    def analyze_system(initial_state=None, sequence_size=100000, skip=1000, entropy=None):
        """
        Analyze the hyperchaotic system using NIST tests.
        
        Args:
            initial_state: Initial values for the chaotic system [x, y, w, u, v]
            sequence_size: Size of sequence to generate for testing
            skip: Number of initial points to skip (transient)
            entropy: Optional user-provided entropy string
            
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
        results = NISTTestSuite.test_randomness(sequence)
        
        return {
            "system": "HyperchaosSystem",
            "sequence_size": sequence_size,
            "skip": skip,
            "test_results": results
        }
    
    @staticmethod
    def analyze_sequence(sequence):
        """
        Analyze an existing byte sequence using NIST tests.
        
        Args:
            sequence: Byte sequence to analyze
            
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
        results = NISTTestSuite.test_randomness(sequence)
        
        return {
            "sequence_size": len(sequence),
            "test_results": results
        }

    @staticmethod
    def analyze_ciphertext(ciphertext, sample_size=None):
        """
        Analyze ciphertext data using NIST tests.

        Args:
            ciphertext: Encrypted data bytes
            sample_size: Number of bytes to use for testing (None = use all)

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
        results = NISTTestSuite.test_randomness(sequence)

        return {
            "sequence_size": len(sequence),
            "test_results": results
        }