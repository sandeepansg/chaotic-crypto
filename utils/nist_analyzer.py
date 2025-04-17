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
