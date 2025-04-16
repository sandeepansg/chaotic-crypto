"""
Secure random number generation using hyperchaotic systems.
"""
import random
import time
import hashlib
from chaos.chaotic import ChaoticSystem

class SecureRandom:
    """Provides secure random number generation using the hyperchaotic system."""
    
    @staticmethod
    def seed_random(entropy=None):
        """Seed the random number generator."""
        if entropy:
            seed_value = hash(f"{entropy}{time.time()}")
            random.seed(seed_value)
        else:
            random.seed(time.time())
    
    @staticmethod
    def randint(a, b, entropy=None):
        """Generate random integer between a and b (inclusive)."""
        SecureRandom.seed_random(entropy)
        return random.randint(a, b)
    
    @staticmethod
    def chaotic_randint(a, b, entropy=None, initial_state=None):
        """Generate random integer using hyperchaotic system."""
        # Generate initial state from entropy if provided
        if entropy and not initial_state:
            initial_state = SecureRandom.generate_initial_state(entropy)
        elif not initial_state:
            initial_state = [0.1, 0.2, 0.3, 0.4, 0.5]  # Default values
            
        # Generate 8 bytes of chaotic data
        sequence = ChaoticSystem.generate_bytes(initial_state, 8)
        
        # Use 8 bytes as a large random value
        value = int.from_bytes(sequence, byteorder='big')
        
        # Scale to range [a, b]
        return a + (value % (b - a + 1))
    
    @staticmethod
    def generate_initial_state(entropy):
        """Generate initial state values for hyperchaotic system from entropy string."""
        # Combine entropy with timestamp to ensure uniqueness
        seed_data = f"{entropy}{time.time()}"
        
        # Use SHA-256 to create deterministic but unpredictable hash
        h = hashlib.sha256(seed_data.encode()).digest()
        
        # Extract 5 values from hash and normalize to [0,1] range
        initial_state = []
        for i in range(0, 20, 4):
            value = int.from_bytes(h[i:i+4], byteorder='big')
            normalized = (value / 2**32) * 0.9 + 0.05
            initial_state.append(normalized)
            
        return initial_state
    
    @staticmethod
    def generate_bytes(size, entropy=None):
        """Generate random bytes using hyperchaotic system."""
        # Generate initial state from entropy
        initial_state = SecureRandom.generate_initial_state(entropy) if entropy else None
        
        # Generate bytes using the system
        return ChaoticSystem.generate_bytes(initial_state, size)
