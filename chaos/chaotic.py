"""
Interface module for the chaos-related components.
This module provides a unified interface to the hyperchaotic system
and Chebyshev polynomial functionality.
"""
from chaos.attractor import HyperchaosSystem
from chaos.chebyshev import ChebyshevPoly


class ChaosInterface:
    """Unified interface to the chaos-related functionality."""
    
    @staticmethod
    def create_hyperchaos_system(k1=1.0, k2=4.0, k3=1.2):
        """Create an instance of the hyperchaotic system with the given parameters."""
        # Validate parameters
        k1 = max(0.1, min(k1, 10.0))  # Reasonable range for k1
        k2 = max(1.0, min(k2, 20.0))  # Reasonable range for k2
        k3 = max(0.1, min(k3, 5.0))   # Reasonable range for k3
        
        return HyperchaosSystem(k1, k2, k3)
    
    @staticmethod
    def create_chebyshev_calculator(modulus):
        """Create an instance of the Chebyshev polynomial calculator."""
        # Ensure modulus is positive
        modulus = max(2, modulus)
        return ChebyshevPoly(modulus)
    
    @staticmethod
    def generate_sequence(initial_state, time_span, num_points=1000):
        """Generate a chaotic sequence using default parameters."""
        # Validate parameters
        if len(initial_state) < 5:
            initial_state = initial_state + [0.1] * (5 - len(initial_state))
        
        time_span = (min(time_span), max(time_span))
        num_points = max(10, min(num_points, 100000))  # Reasonable limits
        
        system = HyperchaosSystem()
        return system.generate_sequence(initial_state, time_span, num_points)
    
    @staticmethod
    def generate_keystream(initial_state, length, skip=100):
        """Generate a keystream using default parameters."""
        # Validate parameters
        if len(initial_state) < 5:
            initial_state = initial_state + [0.1] * (5 - len(initial_state))
        
        length = max(1, length)
        skip = max(50, skip)  # Ensure minimum skip for chaotic stability
        
        system = HyperchaosSystem()
        return system.generate_keystream(initial_state, length, skip)
    
    @staticmethod
    def generate_bytes(initial_state, num_bytes, skip=100):
        """Generate a byte sequence using default parameters."""
        # Validate parameters
        if len(initial_state) < 5:
            initial_state = initial_state + [0.1] * (5 - len(initial_state))
        
        num_bytes = max(1, num_bytes)
        skip = max(50, skip)  # Ensure minimum skip for chaotic stability
        
        system = HyperchaosSystem()
        return system.generate_bytes(initial_state, num_bytes, skip)
    
    @staticmethod
    def generate_block(initial_state, block_size, num_blocks=1, skip=100):
        """Generate blocks of bytes using default parameters."""
        # Validate parameters
        if len(initial_state) < 5:
            initial_state = initial_state + [0.1] * (5 - len(initial_state))
        
        block_size = max(1, block_size)
        num_blocks = max(1, num_blocks)
        skip = max(50, skip)  # Ensure minimum skip for chaotic stability
        
        system = HyperchaosSystem()
        return system.generate_block(initial_state, block_size, num_blocks, skip)
    
    @staticmethod
    def evaluate_chebyshev(degree, x, modulus):
        """Evaluate a Chebyshev polynomial."""
        # Validate parameters
        degree = max(0, degree)
        modulus = max(2, modulus)
        
        poly = ChebyshevPoly(modulus)
        return poly.eval(degree, x)


# Create a singleton instance for easier imports
ChaoticSystem = ChaosInterface()
