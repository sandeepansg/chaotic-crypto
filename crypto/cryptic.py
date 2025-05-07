"""Interface module for cryptographic components."""
from crypto.security import SecurityParams
from crypto.dh import ChebyshevDH
from crypto.feistel import HyperchaosBlockCipher
from crypto.sbox import HyperchaosBoxGenerator


class CryptoInterface:
    """Unified interface to cryptographic functionality."""

    @staticmethod
    def get_security_params(private_bits=None):
        return SecurityParams.get_secure_params(private_bits)

    @staticmethod
    def validate_feistel_params(rounds=None, block_size=None):
        return SecurityParams.validate_feistel_params(rounds, block_size)

    @staticmethod
    def validate_dh_params(private_bits=None):
        return SecurityParams.validate_dh_params(private_bits)

    @staticmethod
    def validate_sbox_params(box_size=None):
        return SecurityParams.validate_sbox_params(box_size)

    @staticmethod
    def create_dh_exchange(private_bits=32):
        return ChebyshevDH(private_bits)

    @staticmethod
    def create_sbox_generator(shared_secret, box_size=256):
        return HyperchaosBoxGenerator(shared_secret, box_size)

    @staticmethod
    def create_block_cipher(sbox, rounds=16, block_size=8):
        return HyperchaosBlockCipher(sbox, rounds, block_size)

    @staticmethod
    def simulate_key_exchange(dh_instance, alice_entropy=None, bob_entropy=None):
        return dh_instance.simulate_exchange(alice_entropy, bob_entropy)

    @staticmethod
    def encrypt_data(cipher_instance, plaintext, key=None):
        return cipher_instance.encrypt(plaintext, key)

    @staticmethod
    def decrypt_data(cipher_instance, ciphertext, key=None):
        return cipher_instance.decrypt(ciphertext, key)


# Singleton instance for easier imports
CryptoSystem = CryptoInterface()