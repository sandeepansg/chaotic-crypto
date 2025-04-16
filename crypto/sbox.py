"""
S-box generation using the hyperchaotic system.
"""
import hashlib
from chaos.chaotic import ChaoticSystem
from utils.random_gen import SecureRandom


class HyperchaosBoxGenerator:
    """Generates S-boxes from shared secrets using hyperchaotic system."""

    def __init__(self, shared_secret, box_size=256):
        """Initialize with a shared secret to generate S-boxes."""
        self.box_size = box_size
        self.shared_secret = shared_secret
        
        # Convert shared secret to bytes at initialization to avoid repetition
        self.secret_bytes = self.shared_secret.to_bytes(
            (self.shared_secret.bit_length() + 7) // 8, 
            byteorder='big'
        )
        
    def _generate_initial_state(self):
        """Generate initial state for chaotic system from shared secret."""
        # Generate hash of the secret to create initial conditions
        hash_obj = hashlib.sha256(self.secret_bytes)
        hash_digest = hash_obj.digest()
        
        # Convert hash to five float values for initial state
        initial_state = []
        for i in range(0, min(20, len(hash_digest)), 4):
            value = int.from_bytes(hash_digest[i:i+4], byteorder='big')
            # Normalize to [-1, 1] range for the chaotic system
            normalized = (value / (2**32 - 1)) * 2 - 1
            initial_state.append(normalized)
            
        # Ensure we have 5 values
        while len(initial_state) < 5:
            initial_state.append(0.1)
            
        return initial_state
        
    def generate(self):
        """Generate an S-box using the hyperchaotic system with shared secret as seed."""
        # Get initial state from shared secret
        initial_state = self._generate_initial_state()
            
        # Generate a chaotic sequence
        trajectory = ChaoticSystem.generate_sequence(
            initial_state, 
            (0, 10), 
            num_points=self.box_size * 2
        )
        
        # Initialize S-box with identity mapping
        sbox = list(range(self.box_size))
        
        # Fisher-Yates shuffle using the chaotic sequence
        x_values = trajectory[0, :]
        y_values = trajectory[1, :]
        
        for i in range(self.box_size - 1, 0, -1):
            # Combine chaotic values to determine swap index
            combined_value = abs(x_values[i] + y_values[i])
            # Scale to range [0, i]
            swap_index = int(combined_value * (i + 1)) % (i + 1)
            
            # Swap elements
            sbox[i], sbox[swap_index] = sbox[swap_index], sbox[i]
            
        return sbox
        
    def generate_with_avalanche(self):
        """Generate an S-box with good avalanche characteristics."""
        # Generate a base S-box
        sbox = self.generate()
        
        # Get initial state from shared secret
        initial_state = self._generate_initial_state()
        
        # Additional chaotic mixing to improve avalanche effect
        for i in range(self.box_size - 1, 0, -1):
            # Use SecureRandom with our initial state for deterministic but chaotic behavior
            swap_index = SecureRandom.chaotic_randint(0, i, initial_state=initial_state)
            sbox[i], sbox[swap_index] = sbox[swap_index], sbox[i]
            
            # Modify initial state slightly for next iteration
            initial_state[0] += 0.01
            initial_state[0] %= 1.0
        
        return sbox
