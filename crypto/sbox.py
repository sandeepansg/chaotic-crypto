"""S-box generation using the hyperchaotic system."""
import hashlib
from chaos.chaotic import ChaoticSystem
from utils.random_gen import SecureRandom


class HyperchaosBoxGenerator:
    """Generates S-boxes from shared secrets using hyperchaotic system."""

    def __init__(self, shared_secret, box_size=256):
        self.box_size = box_size
        self.shared_secret = shared_secret
        
    def generate(self):
        # Convert shared secret to bytes
        secret_bytes = self.shared_secret.to_bytes(
            (self.shared_secret.bit_length() + 7) // 8, 
            byteorder='big'
        )
        
        # Generate hash of the secret to create initial conditions
        hash_obj = hashlib.sha256(secret_bytes)
        hash_digest = hash_obj.digest()
        
        # Convert first 20 bytes of hash to 5 float values for initial state
        initial_state = []
        for i in range(0, min(20, len(hash_digest)), 4):
            value = int.from_bytes(hash_digest[i:i+4], byteorder='big')
            normalized = (value / (2**32 - 1)) * 2 - 1
            initial_state.append(normalized)
            
        # Ensure we have 5 values
        while len(initial_state) < 5:
            initial_state.append(0.1)
            
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
            j_float = abs(x_values[i] + y_values[i])
            j_int = int(j_float * (i + 1)) % (i + 1)
            
            # Swap elements
            sbox[i], sbox[j_int] = sbox[j_int], sbox[i]
            
        return sbox
        
    def generate_with_avalanche(self):
        # Generate a base S-box
        base_sbox = self.generate()
        
        # Use SecureRandom to introduce additional entropy
        for i in range(len(base_sbox) - 1, 0, -1):
            j = SecureRandom.chaotic_randint(0, i, [0.1, 0.2, 0.3, 0.4, 0.5])
            base_sbox[i], base_sbox[j] = base_sbox[j], base_sbox[i]
        
        return base_sbox
