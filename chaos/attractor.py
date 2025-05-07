"""Hyperchaotic system with four-wing attractors for cryptography."""
import numpy as np
from scipy.integrate import solve_ivp


class HyperchaosSystem:
    """Implements a hyperchaotic system with four-wing attractors."""

    def __init__(self, k1=1.0, k2=4.0, k3=1.2):
        self.k1, self.k2, self.k3 = k1, k2, k3

    def _system_equations(self, t, state):
        x, y, w, u, v = state

        dx = 10 * (y - x) + u
        dy = 28 * x - y - x * (w**2) - v
        dw = self.k1 * x * y * w - self.k2 * w + self.k3 * v
        du = -x * (w**2) + 2 * u
        dv = 8 * y

        return [dx, dy, dw, du, dv]

    def generate_sequence(self, initial_state, t_span, num_points=1000):
        t_eval = np.linspace(t_span[0], t_span[1], num_points)
        solution = solve_ivp(
            self._system_equations,
            t_span,
            initial_state,
            t_eval=t_eval,
            method='RK45'
        )
        return solution.y

    def generate_keystream(self, initial_state, length, skip=100):
        t_span = (0, (length + skip) * 0.01)
        trajectory = self.generate_sequence(initial_state, t_span, length + skip)
        return trajectory[:, skip:][:, :length]

    def generate_bytes(self, initial_state, num_bytes, skip=100):
        keystream = self.generate_keystream(initial_state, num_bytes, skip)
        x_values, y_values = keystream[0, :], keystream[1, :]

        byte_array = bytearray()
        for i in range(num_bytes):
            value = int(abs((x_values[i] + y_values[i]) * 100) % 256)
            byte_array.append(value)

        return bytes(byte_array)

    def generate_block(self, initial_state, block_size, num_blocks=1, skip=100):
        total_bytes = block_size * num_blocks
        byte_sequence = self.generate_bytes(initial_state, total_bytes, skip)

        blocks = []
        for i in range(0, total_bytes, block_size):
            blocks.append(byte_sequence[i:i+block_size])

        return blocks