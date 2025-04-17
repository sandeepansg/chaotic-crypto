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
        return SecurityParams.validate_feistel_params(rounds, block_size)
    
    @staticmethod
    def validate_dh_params(private_bits=None):
        """Validate and adjust Diffie-Hellman parameters."""
        return SecurityParams.validate_dh_params(private_bits)
    
    @staticmethod
    def validate_sbox_params(box_size=None):
        """Validate and adjust S-box parameters."""
        return SecurityParams.validate_sbox_params(box_size)
    
    @staticmethod
    def create_dh_exchange(private_bits=32):
        """Create a Diffie-Hellman key exchange with the given parameters."""
        return ChebyshevDH(private_bits)
    
    @staticmethod
    def create_sbox_generator(shared_secret, box_size=256):
        """Create an S-box generator with the given parameters."""
        return HyperchaosBoxGenerator(shared_secret, box_size)
    
    @staticmethod
    def create_block_cipher(sbox, rounds=16, block_size=8):
        """Create a hyperchaotic block cipher with the given parameters."""
        return HyperchaosBlockCipher(sbox, rounds, block_size)
    
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
