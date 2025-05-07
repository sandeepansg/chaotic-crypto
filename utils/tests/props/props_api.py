"""API for mathematical property testing."""
from utils.tests.props.chebyshev_tests import ChebyshevTests
from utils.tests.props.hyperchaos_tests import HyperchaosTests
from utils.tests.props.crypto_tests import CryptoTests


class PropTestingAPI:
    """API for testing mathematical properties of cryptography components."""
    
    @staticmethod
    def test_chebyshev(modulus=None, test_type="all"):
        """
        Run tests on Chebyshev polynomial implementation.
        
        Args:
            modulus: Optional modulus to use for testing
            test_type: Type of test(s) to run ("all", "semigroup", "commutativity", 
                      "associativity", "avalanche")
                      
        Returns:
            Dict containing test results
        """
        tester = ChebyshevTests(modulus)
        
        if test_type == "all":
            return tester.run_all_tests()
        elif test_type == "semigroup":
            return tester.test_semigroup_property()
        elif test_type == "commutativity":
            return tester.test_commutativity()
        elif test_type == "associativity":
            return tester.test_associativity()
        elif test_type == "avalanche":
            return tester.test_avalanche_effect()
        else:
            raise ValueError(f"Unknown test type: {test_type}")

    @staticmethod
    def test_hyperchaos(k1=1.0, k2=4.0, k3=1.2, test_type="all"):
        """
        Run tests on hyperchaotic system implementation.

        Args:
            k1, k2, k3: Parameters for the hyperchaotic system
            test_type: Type of test(s) to run ("all", "avalanche", "byte_avalanche",
                      "sensitivity")

        Returns:
            Dict containing test results
        """
        tester = HyperchaosTests(k1, k2, k3)

        if test_type == "all":
            return tester.run_all_tests()
        elif test_type == "avalanche":
            return tester.test_avalanche_effect()
        elif test_type == "byte_avalanche":
            return tester.test_byte_generation_avalanche()
        elif test_type == "sensitivity":
            return tester.test_sensitivity()
        else:
            raise ValueError(f"Unknown test type: {test_type}")

    @staticmethod
    def test_crypto(test_type="all", **kwargs):
        """
        Run tests on cryptographic components.

        Args:
            test_type: Type of test(s) to run ("all", "sbox_avalanche",
                      "cipher_avalanche", "dh_sensitivity")
            **kwargs: Additional parameters for specific tests

        Returns:
            Dict containing test results
        """
        tester = CryptoTests()

        if test_type == "all":
            return tester.run_all_tests()
        elif test_type == "sbox_avalanche":
            box_size = kwargs.get("box_size", 256)
            shared_secret = kwargs.get("shared_secret", None)
            return tester.test_sbox_avalanche(box_size, shared_secret)
        elif test_type == "cipher_avalanche":
            sbox = kwargs.get("sbox", None)
            rounds = kwargs.get("rounds", 16)
            block_size = kwargs.get("block_size", 8)
            return tester.test_block_cipher_avalanche(sbox, rounds, block_size)
        elif test_type == "dh_sensitivity":
            private_bits = kwargs.get("private_bits", 16)
            return tester.test_dh_key_sensitivity(private_bits)
        else:
            raise ValueError(f"Unknown test type: {test_type}")

    @staticmethod
    def run_all_tests(**kwargs):
        """
        Run all mathematical property tests.

        Args:
            **kwargs: Additional parameters for specific tests

        Returns:
            Dict containing all test results
        """
        results = {
            "chebyshev": PropTestingAPI.test_chebyshev(
                modulus=kwargs.get("modulus", None)
            ),
            "hyperchaos": PropTestingAPI.test_hyperchaos(
                k1=kwargs.get("k1", 1.0),
                k2=kwargs.get("k2", 4.0),
                k3=kwargs.get("k3", 1.2)
            ),
            "crypto": PropTestingAPI.test_crypto()
        }

        return results