"""Test properties of Chebyshev polynomials implementation."""
from utils.tests.props.properties import MathProperties
from chaos.chebyshev import ChebyshevPoly
import random


class ChebyshevTests:
    """Provides tests for mathematical properties of Chebyshev polynomials."""
    
    def __init__(self, modulus=None):
        """
        Initialize test suite for Chebyshev polynomials.
        
        Args:
            modulus: The modulus for the Chebyshev polynomial calculations
        """
        self.modulus = modulus or 1031  # Small prime by default
        self.cheby = ChebyshevPoly(self.modulus)
        
    def generate_test_samples(self, count=10, max_degree=20):
        """
        Generate test samples for Chebyshev polynomial tests.
        
        Args:
            count: Number of sample points to generate
            max_degree: Maximum polynomial degree to test
            
        Returns:
            Dict containing test samples
        """
        # Generate random x values in the field
        x_values = [random.randint(0, self.modulus-1) for _ in range(count)]
        
        # Generate random degrees
        degrees = list(range(2, max_degree+1))
        
        return {
            "modulus": self.modulus,
            "x_values": x_values,
            "degrees": degrees
        }
        
    def test_semigroup_property(self, samples=None):
        """
        Test if Chebyshev polynomial composition forms a semigroup.
        
        Args:
            samples: Optional dict with test samples
            
        Returns:
            Dict containing test results
        """
        if samples is None:
            samples = self.generate_test_samples()
            
        # Create composition operation using fixed x
        x = samples["x_values"][0]
        
        def compose(n, m):
            """Chebyshev polynomial composition operation."""
            # T_n(T_m(x)) = T_{n*m}(x) property
            return self.cheby.eval(n * m, x) % self.modulus
            
        return MathProperties.test_semigroup(compose, samples["degrees"])
        
    def test_commutativity(self, samples=None):
        """
        Test if Chebyshev polynomial composition is commutative.
        
        Args:
            samples: Optional dict with test samples
            
        Returns:
            Dict containing test results
        """
        if samples is None:
            samples = self.generate_test_samples()
            
        # Create composition operation using fixed x
        x = samples["x_values"][0]
        
        def compose(n, m):
            """Chebyshev polynomial composition operation."""
            return self.cheby.eval(n * m, x) % self.modulus
            
        return MathProperties.test_commutativity(compose, samples["degrees"])
    
    def test_associativity(self, samples=None):
        """
        Test if Chebyshev polynomial composition is associative.
        
        Args:
            samples: Optional dict with test samples
            
        Returns:
            Dict containing test results
        """
        if samples is None:
            samples = self.generate_test_samples()
            
        # Create composition operation using fixed x
        x = samples["x_values"][0]
        
        def compose(n, m):
            """Chebyshev polynomial composition operation."""
            return self.cheby.eval(n * m, x) % self.modulus
            
        return MathProperties.test_associativity(compose, samples["degrees"])
    
    def test_avalanche_effect(self, samples=None):
        """
        Test the avalanche effect of Chebyshev polynomials.
        
        Args:
            samples: Optional dict with test samples
            
        Returns:
            Dict containing avalanche test results
        """
        if samples is None:
            samples = self.generate_test_samples(count=20)
        
        # Create testing function with fixed degree
        degree = 17  # Prime number for better testing
        
        def eval_fn(x):
            """Evaluate Chebyshev polynomial at a point."""
            return self.cheby.eval(degree, x)
        
        # Generate inputs as integers
        inputs = [x for x in samples["x_values"]]
        
        # Test bit positions that make sense for the modulus size
        bit_positions = [0, 1, 2, 4, 8]
        
        return MathProperties.test_avalanche(eval_fn, inputs, bit_positions)
    
    def run_all_tests(self):
        """
        Run all Chebyshev polynomial tests.
        
        Returns:
            Dict containing all test results
        """
        samples = self.generate_test_samples(count=15, max_degree=30)
        
        results = {
            "modulus": self.modulus,
            "semigroup": self.test_semigroup_property(samples),
            "commutativity": self.test_commutativity(samples),
            "associativity": self.test_associativity(samples),
            "avalanche": self.test_avalanche_effect(samples)
        }
        
        return results
