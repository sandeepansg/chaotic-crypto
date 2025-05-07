"""Diffie-Hellman key exchange using Chebyshev polynomials."""
import sympy
from chaos.chaotic import ChaoticSystem
from utils.random_gen import SecureRandom


class ChebyshevDH:
    """Diffie-Hellman key exchange using Chebyshev polynomials."""

    def __init__(self, private_bits=32):
        self.private_bits = private_bits
        prime_bits = max(256, private_bits * 4)
        self.public_bits = min(private_bits * 2, prime_bits - 1)
        param_bits = prime_bits - 1

        self.mod = sympy.randprime(2 ** (prime_bits - 1), 2 ** prime_bits)
        self.cheby = ChaoticSystem.create_chebyshev_calculator(self.mod)
        self.param = SecureRandom.randint(2 ** (param_bits - 1), 2 ** param_bits - 1)

    def generate_keypair(self, entropy=None):
        private_min = 2 ** (self.private_bits - 1)
        private_max = 2 ** self.private_bits - 1
        private = SecureRandom.randint(private_min, private_max, entropy)

        raw_public = self.cheby.eval(private, self.param)

        mask = (2 ** self.public_bits) - 1
        public = (raw_public & mask) | (2 ** (self.public_bits - 1))
        public %= self.mod

        return private, public, raw_public

    def compute_shared(self, private, other_public):
        return self.cheby.eval(private, other_public)

    def simulate_exchange(self, alice_entropy=None, bob_entropy=None):
        alice_priv, alice_pub, alice_raw = self.generate_keypair(alice_entropy)
        bob_priv, bob_pub, bob_raw = self.generate_keypair(bob_entropy)

        alice_shared = self.compute_shared(alice_priv, bob_raw)
        bob_shared = self.compute_shared(bob_priv, alice_raw)

        return {
            "alice_private": alice_priv,
            "alice_public": alice_pub,
            "alice_raw_public": alice_raw,
            "bob_private": bob_priv,
            "bob_public": bob_pub,
            "bob_raw_public": bob_raw,
            "alice_shared": alice_shared,
            "bob_shared": bob_shared,
            "match": alice_shared == bob_shared
        }

    def get_system_info(self):
        return {
            "mod": self.mod,
            "mod_bits": self.mod.bit_length() if self.mod is not None else 0,
            "param": self.param,
            "param_bits": self.param.bit_length() if self.param is not None else 0,
            "private_bits": self.private_bits,
            "public_bits": self.public_bits
        }