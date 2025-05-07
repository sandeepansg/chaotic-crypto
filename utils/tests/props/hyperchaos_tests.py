"""Test properties of the hyperchaotic system implementation."""
from utils.tests.props.properties import MathProperties
from chaos.attractor import HyperchaosSystem
import numpy as np


class HyperchaosTests:
    """Provides tests for mathematical properties of hyperchaotic systems."""
    
    def __init__(self, k1=1.0, k2=4.0, k3=1.2):
        """
        Initialize test suite for hyperchaotic systems.
        
        Args:
            k1, k2, k3: Parameters for the hyperchaotic system
        """
        self.system = HyperchaosSystem(k1, k2, k3)
    
    def generate_test_samples(self, count=10):
        """
        Generate test samples for hyperchaotic system tests.
        
        Args:
            count: Number of sample initial states to generate
            
        Returns:
            Dict containing test samples
        """
        # Generate random initial states
        samples = []
        for _ in range(count):
            state = [np.random.uniform(-1, 1) for _ in range(5)]
            samples.append(state)
            
        return {
            "initial_states": samples,
            "t_span": (0, 0.1),
            "num_points": 100
        }
    
    def test_avalanche_effect(self, samples=None):
        """
        Test the avalanche effect of the hyperchaotic system.
        
        Args:
            samples: Optional dict with test samples
            
        Returns:
            Dict containing test results
        """
        if samples is None:
            samples = self.generate_test_samples()
        
        def generate_sequence_fn(initial_state):
            """Generate sequence from initial state."""
            sequence = self.system.generate_sequence(
                initial_state, 
                samples["t_span"], 
                samples["num_points"]
            )
            # Return flattened array for easier comparison
            return sequence.flatten().tolist()
        
        # Test with various initial states
        inputs = samples["initial_states"]
        
        # For floating point values, we're interested in small changes
        # These are indices in the initial state array where we'll make changes
        bit_positions = [0, 1, 2, 3, 4]
        
        return MathProperties.test_avalanche(generate_sequence_fn, inputs, bit_positions)
    
    def test_byte_generation_avalanche(self, samples=None):
        """
        Test the avalanche effect in byte generation.
        
        Args:
            samples: Optional dict with test samples
            
        Returns:
            Dict containing test results
        """
        if samples is None:
            samples = self.generate_test_samples(count=5)
        
        def generate_bytes_fn(initial_state):
            """Generate bytes from initial state."""
            return self.system.generate_bytes(initial_state, 32, skip=10)
        
        # Test with various initial states
        inputs = samples["initial_states"]
        
        # These are indices in the initial state array where we'll make changes
        bit_positions = [0, 1, 2, 3, 4]
        
        return MathProperties.test_avalanche(generate_bytes_fn, inputs, bit_positions)
    
    def test_sensitivity(self, samples=None):
        """
        Test sensitivity to initial conditions.
        
        Args:
            samples: Optional dict with test samples
            
        Returns:
            Dict containing sensitivity test results
        """
        if samples is None:
            samples = self.generate_test_samples(count=3)
        
        results = {
            "property": "sensitivity", 
            "samples": [],
            "summary": {}
        }
        
        all_divergences = []
        
        for state in samples["initial_states"]:
            # Create a slightly modified state
            modified_state = state.copy()
            modified_state[0] += 1e-10  # Very small change
            
            # Generate sequences
            orig_seq = self.system.generate_sequence(
                state, (0, 1.0), 500
            )
            mod_seq = self.system.generate_sequence(
                modified_state, (0, 1.0), 500
            )
            
            # Calculate differences over time
            differences = []
            for t in range(orig_seq.shape[1]):
                point1 = orig_seq[:, t]
                point2 = mod_seq[:, t]
                diff = np.linalg.norm(point1 - point2)
                differences.append(diff)
            
            # Find where differences exceed threshold
            threshold = 0.1
            exceed_index = next((i for i, d in enumerate(differences) if d > threshold), -1)
            
            # Calculate divergence rate
            if exceed_index > 0:
                time_to_diverge = exceed_index * (1.0 / 500)
                all_divergences.append(time_to_diverge)
            
            # Save sample data
            if len(results["samples"]) < 3:
                sample_data = {
                    "original": state,
                    "modified": modified_state,
                    "final_difference": differences[-1],
                    "divergence_time": exceed_index * (1.0 / 500) if exceed_index > 0 else "N/A"
                }
                results["samples"].append(sample_data)
        
        # Calculate summary statistics
        if all_divergences:
            results["summary"]["avg_divergence_time"] = np.mean(all_divergences)
            results["summary"]["min_divergence_time"] = np.min(all_divergences)
            results["summary"]["max_divergence_time"] = np.max(all_divergences)
        
        # A chaotic system should have rapid divergence
        results["passed"] = results["summary"].get("avg_divergence_time", float('inf')) < 0.5
        
        return results
    
    def run_all_tests(self):
        """
        Run all hyperchaotic system tests.
        
        Returns:
            Dict containing all test results
        """
        samples = self.generate_test_samples(count=5)
        
        results = {
            "avalanche": self.test_avalanche_effect(samples),
            "byte_avalanche": self.test_byte_generation_avalanche(samples),
            "sensitivity": self.test_sensitivity(samples)
        }
        
        return results
