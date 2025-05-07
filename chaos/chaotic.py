"""Interface module for chaos-related components."""
from chaos.attractor import HyperchaosSystem
from chaos.chebyshev import ChebyshevPoly


class ChaosInterface:
    """Unified interface to chaos functionality."""

    @staticmethod
    def create_hyperchaos_system(k1=1.0, k2=4.0, k3=1.2):
        return HyperchaosSystem(k1, k2, k3)

    @staticmethod
    def create_chebyshev_calculator(modulus):
        return ChebyshevPoly(modulus)

    @staticmethod
    def generate_sequence(initial_state, t_span, num_points=1000):
        return HyperchaosSystem().generate_sequence(initial_state, t_span, num_points)

    @staticmethod
    def generate_keystream(initial_state, length, skip=100):
        return HyperchaosSystem().generate_keystream(initial_state, length, skip)

    @staticmethod
    def generate_bytes(initial_state, num_bytes, skip=100):
        return HyperchaosSystem().generate_bytes(initial_state, num_bytes, skip)

    @staticmethod
    def generate_block(initial_state, block_size, num_blocks=1, skip=100):
        return HyperchaosSystem().generate_block(initial_state, block_size, num_blocks, skip)

    @staticmethod
    def evaluate_chebyshev(degree, x, modulus):
        return ChebyshevPoly(modulus).eval(degree, x)


# Singleton instance for easier imports
ChaoticSystem = ChaosInterface()