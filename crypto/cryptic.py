"""
Interface module for the cryptographic components.
This module provides a unified interface to the Diffie-Hellman key exchange,
Feistel cipher, S-box generation, and security parameter management.
"""
from crypto.security import SecurityParams
from crypto.dh import ChebyshevDH
from crypto.feistel import HyperchaosBlockCipher
from crypto.sbox import HyperchaosBoxGenerator
from chaos.chaotic import ChaoticSystem


class CryptoInterface:
    """Unified interface to the cryptographic functionality."""
    
    @staticmethod
    def get_security_params(private_bits=None):
        """Get appropriate security parameters based on private key length."""
        return SecurityParams.get_secure_params(private_bits)
    
    @staticmethod
    def validate_feistel_params(rounds=None, block_size=None):
        """Validate and adjust Feistel cipher parameters."""
        # Use defaults if not provided
        rounds = rounds if rounds is not None else SecurityParams.DEFAULT_FEISTEL_ROUNDS
        block_size = block_size if block_size is not None else SecurityParams.DEFAULT_BLOCK_SIZE
        
        # Enforce minimum and maximum values
        rounds = max(rounds, SecurityParams.MIN_FEISTEL_ROUNDS)
        block_size = max(min(block_size, SecurityParams.MAX_BLOCK_SIZE), SecurityParams.MIN_BLOCK_SIZE)
        
        # Ensure block_size is even for Feistel structure
        if block_size % 2 != 0:
            block_size += 1
            
        return {
            "rounds": rounds,
            "block_size": block_size
        }
    
    @staticmethod
    def validate_dh_params(private_bits=None):
        """Validate and adjust Diffie-Hellman parameters."""
        # Use default if not provided
        private_bits = private_bits if private_bits is not None else SecurityParams.DEFAULT_PRIVATE_BITS
        
        # Enforce limits
        private_bits = max(min(private_bits, SecurityParams.MAX_PRIVATE_BITS), SecurityParams.MIN_PRIVATE_BITS)
        
        return SecurityParams.get_secure_params(private_bits)
    
    @staticmethod
    def validate_sbox_params(box_size=None):
        """Validate and adjust S-box parameters."""
        # Use default if not provided
        box_size = box_size if box_size is not None else SecurityParams.DEFAULT_SBOX_SIZE
        
        # Enforce minimum and maximum values
        box_size = max(min(box_size, SecurityParams.MAX_SBOX_SIZE), SecurityParams.MIN_SBOX_SIZE)
        
        # Find the nearest power of 2 that's >= box_size
        power = 1
        while power < box_size:
            power *= 2
            
        return {
            "box_size": power
        }
    
    @staticmethod
    def create_dh_exchange(private_bits=32):
        """Create a Diffie-Hellman key exchange with the given parameters."""
        # Validate parameters
        private_bits = max(SecurityParams.MIN_PRIVATE_BITS, 
                          min(private_bits, SecurityParams.MAX_PRIVATE_BITS))
        return ChebyshevDH(private_bits)
    
    @staticmethod
    def create_sbox_generator(shared_secret, box_size=256):
        """Create an S-box generator with the given parameters."""
        # Validate parameters
        box_size_params = CryptoInterface.validate_sbox_params(box_size)
        return HyperchaosBoxGenerator(shared_secret, box_size_params["box_size"])
    
    @staticmethod
    def create_block_cipher(sbox, rounds=16, block_size=8):
        """Create a hyperchaotic block cipher with the given parameters."""
        # Validate parameters
        feistel_params = CryptoInterface.validate_feistel_params(rounds, block_size)
        return HyperchaosBlockCipher(sbox, feistel_params["rounds"], feistel_params["block_size"])
    
    @staticmethod
    def simulate_key_exchange(dh_instance, alice_entropy=None, bob_entropy=None):
        """Simulate a complete key exchange between two parties."""
        return dh_instance.simulate_exchange(alice_entropy, bob_entropy)
    
    @staticmethod
    def encrypt_data(cipher_instance, plaintext, key=None):
        """Encrypt data using the given cipher instance."""
        return cipher_instance.encrypt(plaintext, key)
    
    @staticmethod
    def decrypt_data(cipher_instance, ciphertext, key=None):
        """Decrypt data using the given cipher instance."""
        return cipher_instance.decrypt(ciphertext, key)


# Create a singleton instance for easier imports
CryptoSystem = CryptoInterface()
