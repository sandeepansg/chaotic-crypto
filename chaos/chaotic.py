"""Interface module for the chaos-related components."""
from chaos.attractor import HyperchaosSystem
from chaos.chebyshev import ChebyshevPoly


class ChaosInterface:
    """Unified interface to the chaos-related functionality."""
    
    @staticmethod
    def create_hyperchaos_system(k1=1.0, k2=4.0, k3=1.2):
        return HyperchaosSystem(k1, k2, k3)
    
    @staticmethod
    def create_chebyshev_calculator(modulus):
        return ChebyshevPoly(modulus)
    
    @staticmethod
    def generate_sequence(initial_state, t_span, num_points=1000):
        system = HyperchaosSystem()
        return system.generate_sequence(initial_state, t_span, num_points)
    
    @staticmethod
    def generate_keystream(initial_state, length, skip=100):
        system = HyperchaosSystem()
        return system.generate_keystream(initial_state, length, skip)
    
    @staticmethod
    def generate_bytes(initial_state, num_bytes, skip=100):
        system = HyperchaosSystem()
        return system.generate_bytes(initial_state, num_bytes, skip)
    
    @staticmethod
    def generate_block(initial_state, block_size, num_blocks=1, skip=100):
        system = HyperchaosSystem()
        return system.generate_block(initial_state, block_size, num_blocks, skip)
    
    @staticmethod
    def evaluate_chebyshev(degree, x, modulus):
        poly = ChebyshevPoly(modulus)
        return poly.eval(degree, x)


# Create a singleton instance for easier imports
ChaoticSystem = ChaosInterface()
