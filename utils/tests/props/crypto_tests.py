"""Test properties of cryptographic components."""
from utils.tests.props.properties import MathProperties
from crypto.feistel import HyperchaosBlockCipher
from crypto.sbox import HyperchaosBoxGenerator
from crypto.dh import ChebyshevDH
import random


class CryptoTests:
    """Provides tests for properties of cryptographic components."""
    
    def __init__(self):
        """Initialize test suite for cryptographic components."""
        pass
    
    def test_sbox_avalanche(self, box_size=256, shared_secret=None):
        """
        Test avalanche effect of S-box generation.
        
        Args:
            box_size: Size of the S-box
            shared_secret: Shared secret for S-box generation
            
        Returns:
            Dict containing test results
        """
        if shared_secret is None:
            shared_secret = random.randint(1000000, 9999999)
        
        results = {"property": "sbox_avalanche", "tests": []}
        
        # Test with different shared secrets (varying by small amounts)
        test_secrets = [
            shared_secret,
            shared_secret + 1,
            shared_secret + 2,
            shared_secret + 4,
            shared_secret + 8,
        ]
        
        boxes = []
        for secret in test_secrets:
            generator = HyperchaosBoxGenerator(secret, box_size)
            sbox = generator.generate()
            boxes.append(sbox)
        
        # Compare base S-box with each modified S-box
        base_box = boxes[0]
        differences = []
        
        for i, mod_box in enumerate(boxes[1:]):
            diff_count = sum(1 for a, b in zip(base_box, mod_box) if a != b)
            diff_percent = (diff_count / box_size) * 100
            differences.append(diff_percent)
            
            results["tests"].append({
                "base_secret": shared_secret,
                "modified_secret": test_secrets[i+1],
                "difference_bits": f"{diff_count}/{box_size}",
                "difference_percent": diff_percent
            })
        
        # Calculate summary statistics
        results["summary"] = {
            "avg_difference": sum(differences) / len(differences),
            "min_difference": min(differences),
            "max_difference": max(differences)
        }
        
        # A good S-box generator should produce significantly different boxes
        # even with small input changes
        results["passed"] = results["summary"]["avg_difference"] > 30
        
        return results
    
    def test_block_cipher_avalanche(self, sbox=None, rounds=16, block_size=8):
        """
        Test avalanche effect of block cipher.
        
        Args:
            sbox: S-box to use for testing
            rounds: Number of rounds in the Feistel network
            block_size: Block size in bytes
            
        Returns:
            Dict containing test results
        """
        if sbox is None:
            # Generate a default S-box
            generator = HyperchaosBoxGenerator(12345, 256)
            sbox = generator.generate()
        
        cipher = HyperchaosBlockCipher(sbox, rounds, block_size)
        
        # Generate some test plaintexts
        plaintexts = []
        for _ in range(5):
            plaintexts.append(bytes(random.randint(0, 255) for _ in range(block_size * 2)))
        
        # Define test function that returns ciphertext
        def encrypt_fn(plaintext):
            """Encrypt plaintext using cipher."""
            key = b'testkey12'  # Fixed key for testing
            return cipher.encrypt(plaintext, key)
        
        # Test avalanche effect
        return MathProperties.test_avalanche(encrypt_fn, plaintexts)
    
    def test_dh_key_sensitivity(self, private_bits=16):
        """
        Test sensitivity of DH key exchange to small changes.
        
        Args:
            private_bits: Bit size for private keys
            
        Returns:
            Dict containing test results
        """
        dh = ChebyshevDH(private_bits)
        system_info = dh.get_system_info()
        
        results = {"property": "dh_key_sensitivity", "tests": []}
        
        # Run baseline exchange
        baseline = dh.simulate_exchange("baseline_entropy")
        
        # Run exchanges with small variations in entropy
        variations = [
            "baseline_entropy1",
            "baseline_entropy2",
            "baseline_entropyA",
            "baseline_entropyB"
        ]
        
        shared_secrets = [baseline["alice_shared"]]
        
        for var in variations:
            exchange = dh.simulate_exchange(var)
            shared_secrets.append(exchange["alice_shared"])
            
            # Calculate bit difference with baseline
            xor_result = baseline["alice_shared"] ^ exchange["alice_shared"]
            diff_bits = bin(xor_result).count('1')
            bit_length = max(
                baseline["alice_shared"].bit_length(),
                exchange["alice_shared"].bit_length()
            )
            diff_percent = (diff_bits / bit_length) * 100
            
            results["tests"].append({
                "baseline_entropy": "baseline_entropy",
                "variation_entropy": var,
                "baseline_shared": baseline["alice_shared"],
                "variation_shared": exchange["alice_shared"],
                "difference_bits": f"{diff_bits}/{bit_length}",
                "difference_percent": diff_percent
            })
        
        # Calculate summary statistics from test results
        diff_percentages = [test["difference_percent"] for test in results["tests"]]
        results["summary"] = {
            "avg_difference": sum(diff_percentages) / len(diff_percentages),
            "min_difference": min(diff_percentages),
            "max_difference": max(diff_percentages),
            "private_bits": private_bits,
            "mod_bits": system_info["mod_bits"]
        }
        
        # A secure DH implementation should have significant differences
        results["passed"] = results["summary"]["avg_difference"] > 25
        
        return results
    
    def run_all_tests(self):
        """
        Run all cryptographic component tests.
        
        Returns:
            Dict containing all test results
        """
        results = {
            "sbox_avalanche": self.test_sbox_avalanche(),
            "cipher_avalanche": self.test_block_cipher_avalanche(),
            "dh_sensitivity": self.test_dh_key_sensitivity()
        }
        
        return results
