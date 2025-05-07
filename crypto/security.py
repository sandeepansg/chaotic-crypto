"""Security parameter management for Chebyshev-based cryptosystems."""


class SecurityParams:
    """Centralizes security parameters and their relationships."""

    # Base security constants
    MIN_PRIVATE_BITS = 16
    DEFAULT_PRIVATE_BITS = 32
    MIN_PRIME_BITS = 256
    DEFAULT_PRIME_BITS = 512
    MAX_PRIVATE_BITS = 4096

    # Security scaling factors
    PRIME_TO_PRIVATE_RATIO = 4
    PUBLIC_TO_PRIVATE_RATIO = 2
    
    # Feistel cipher constants
    MIN_FEISTEL_ROUNDS = 8
    DEFAULT_FEISTEL_ROUNDS = 16
    MIN_BLOCK_SIZE = 8
    DEFAULT_BLOCK_SIZE = 8
    MAX_BLOCK_SIZE = 1024

    # S-box constants
    MIN_SBOX_SIZE = 16
    DEFAULT_SBOX_SIZE = 256
    MAX_SBOX_SIZE = 65536

    @classmethod
    def get_secure_params(cls, private_bits=None):
        private_bits = private_bits or cls.DEFAULT_PRIVATE_BITS
        private_bits = max(min(private_bits, cls.MAX_PRIVATE_BITS), cls.MIN_PRIVATE_BITS)

        prime_bits = max(cls.MIN_PRIME_BITS, int(cls.PRIME_TO_PRIVATE_RATIO * private_bits))
        public_bits = min(int(cls.PUBLIC_TO_PRIVATE_RATIO * private_bits), prime_bits - 1)
        param_bits = prime_bits - 1

        return {
            "private_bits": private_bits,
            "prime_bits": prime_bits,
            "public_bits": public_bits,
            "param_bits": param_bits
        }

    @classmethod
    def validate_feistel_params(cls, rounds=None, block_size=None):
        rounds = rounds if rounds is not None else cls.DEFAULT_FEISTEL_ROUNDS
        block_size = block_size if block_size is not None else cls.DEFAULT_BLOCK_SIZE

        rounds = max(rounds, cls.MIN_FEISTEL_ROUNDS)
        block_size = max(min(block_size, cls.MAX_BLOCK_SIZE), cls.MIN_BLOCK_SIZE)

        if block_size % 2 != 0:
            block_size += 1

        return {"rounds": rounds, "block_size": block_size}

    @classmethod
    def validate_dh_params(cls, private_bits=None):
        private_bits = private_bits or cls.DEFAULT_PRIVATE_BITS
        private_bits = max(min(private_bits, cls.MAX_PRIVATE_BITS), cls.MIN_PRIVATE_BITS)
        return cls.get_secure_params(private_bits)

    @classmethod
    def validate_sbox_params(cls, box_size=None):
        box_size = box_size or cls.DEFAULT_SBOX_SIZE
        box_size = max(min(box_size, cls.MAX_SBOX_SIZE), cls.MIN_SBOX_SIZE)

        power = 1
        while power < box_size:
            power *= 2

        return {"box_size": power}