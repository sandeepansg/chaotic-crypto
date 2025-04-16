"""
Implementation of hyperchaotic system with four-wing attractors
for cryptographic applications.
"""
import numpy as np
from scipy.integrate import solve_ivp


class HyperchaosSystem:
    """Implements the hyperchaotic system with four-wing attractors."""

    def __init__(self, k1=1.0, k2=4.0, k3=1.2):
        """Initialize the hyperchaotic system with control parameters."""
        self.k1 = k1
        self.k2 = k2
        self.k3 = k3
        
    def _system_equations(self, t, state):
        """Define the system of differential equations."""
        x, y, w, u, v = state  # Using w as per original code
        
        dx = 10 * (y - x) + u
        dy = 28 * x - y - x * (w**2) - v
        dw = self.k1 * x * y * w - self.k2 * w + self.k3 * v
        du = -x * (w**2) + 2 * u
        dv = 8 * y
        
        return [dx, dy, dw, du, dv]
    
    def generate_sequence(self, initial_state, time_span, num_points=1000):
        """Generate a chaotic sequence by solving the system of equations."""
        time_points = np.linspace(time_span[0], time_span[1], num_points)
        solution = solve_ivp(
            self._system_equations,
            time_span,
            initial_state,
            t_eval=time_points,
            method='RK45'
        )
        
        return solution.y
    
    def generate_keystream(self, initial_state, length, skip=100):
        """Generate a keystream from the chaotic system."""
        # Calculate total required points and appropriate time span
        total_points = length + skip
        time_span = (0, total_points * 0.01)
        
        # Generate full trajectory and skip initial transient points
        trajectory = self.generate_sequence(initial_state, time_span, total_points)
        
        # Return only the requested portion (after skipping)
        return trajectory[:, skip:skip+length]
    
    def generate_bytes(self, initial_state, num_bytes, skip=100):
        """Generate a byte sequence for cryptographic applications."""
        keystream = self.generate_keystream(initial_state, num_bytes, skip)
        
        # Use the first two state variables for byte generation
        x_values = keystream[0, :]
        y_values = keystream[1, :]
        
        # Create bytes with better statistical properties
        byte_array = bytearray()
        for i in range(num_bytes):
            # Improved byte generation with better distribution
            # Use XOR to combine values with multiplication for nonlinearity
            x_abs = abs(x_values[i])
            y_abs = abs(y_values[i])
            value = int((x_abs * 128 + y_abs * 128) % 256)
            byte_array.append(value)
            
        return bytes(byte_array)
    
    def generate_block(self, initial_state, block_size, num_blocks=1, skip=100):
        """Generate blocks of bytes for block cipher applications."""
        total_bytes = block_size * num_blocks
        byte_sequence = self.generate_bytes(initial_state, total_bytes, skip)
        
        # Divide the byte sequence into blocks
        blocks = []
        for i in range(0, total_bytes, block_size):
            block = byte_sequence[i:i+block_size]
            blocks.append(block)
            
        return blocks
