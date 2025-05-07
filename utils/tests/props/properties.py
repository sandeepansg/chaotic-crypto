"""Mathematical properties testing for cryptographic components."""
import numpy as np
from typing import Callable, Dict, List, Tuple, Any, Union


class MathProperties:
    """Tests for mathematical properties of cryptographic components."""

    @staticmethod
    def test_commutativity(operation: Callable, samples: List[Any]) -> Dict:
        """
        Test if an operation is commutative: a * b = b * a.
        
        Args:
            operation: A function taking two arguments
            samples: List of elements to test with
            
        Returns:
            Dict containing commutativity test results
        """
        results = {"property": "commutativity", "passed": True, "failures": []}
        total_tests = 0
        failed_tests = 0
        
        for i, a in enumerate(samples):
            for b in samples[i+1:]:  # Test each pair once
                total_tests += 1
                result1 = operation(a, b)
                result2 = operation(b, a)
                
                if result1 != result2:
                    failed_tests += 1
                    results["passed"] = False
                    if failed_tests <= 5:  # Limit failure examples
                        results["failures"].append({
                            "a": a, "b": b,
                            "a*b": result1, "b*a": result2
                        })
        
        results["total_tests"] = total_tests
        results["failed_tests"] = failed_tests
        results["pass_rate"] = (total_tests - failed_tests) / total_tests if total_tests > 0 else 0
        
        return results

    @staticmethod
    def test_associativity(operation: Callable, samples: List[Any]) -> Dict:
        """
        Test if an operation is associative: (a * b) * c = a * (b * c).
        
        Args:
            operation: A function taking two arguments
            samples: List of elements to test with
            
        Returns:
            Dict containing associativity test results
        """
        results = {"property": "associativity", "passed": True, "failures": []}
        total_tests = 0
        failed_tests = 0
        
        # Use fewer samples if the original list is large
        test_samples = samples[:5] if len(samples) > 5 else samples
        
        for a in test_samples:
            for b in test_samples:
                for c in test_samples:
                    total_tests += 1
                    result1 = operation(operation(a, b), c)
                    result2 = operation(a, operation(b, c))
                    
                    if result1 != result2:
                        failed_tests += 1
                        results["passed"] = False
                        if failed_tests <= 5:  # Limit failure examples
                            results["failures"].append({
                                "a": a, "b": b, "c": c,
                                "(a*b)*c": result1, "a*(b*c)": result2
                            })
        
        results["total_tests"] = total_tests
        results["failed_tests"] = failed_tests
        results["pass_rate"] = (total_tests - failed_tests) / total_tests if total_tests > 0 else 0
        
        return results

    @staticmethod
    def test_semigroup(operation: Callable, samples: List[Any]) -> Dict:
        """
        Test if an operation forms a semigroup:
        - Closed under operation
        - Associative
        
        Args:
            operation: A function taking two arguments
            samples: List of elements to test with
            
        Returns:
            Dict containing semigroup test results
        """
        results = {"property": "semigroup", "passed": True, "components": {}}
        
        # Test closure
        closure_results = MathProperties._test_closure(operation, samples)
        results["components"]["closure"] = closure_results
        
        # Test associativity (using fewer samples if needed)
        test_samples = samples[:5] if len(samples) > 5 else samples
        assoc_results = MathProperties.test_associativity(operation, test_samples)
        results["components"]["associativity"] = assoc_results
        
        # Overall result depends on both properties
        results["passed"] = closure_results["passed"] and assoc_results["passed"]
        
        return results

    @staticmethod
    def _test_closure(operation: Callable, samples: List[Any]) -> Dict:
        """
        Test if an operation is closed: a * b is in the set for all a, b.
        
        Args:
            operation: A function taking two arguments
            samples: List of elements to test with
            
        Returns:
            Dict containing closure test results
        """
        results = {"property": "closure", "passed": True, "failures": []}
        total_tests = 0
        failed_tests = 0
        
        # Create a set of samples for membership testing
        sample_set = set(samples)
        
        for i, a in enumerate(samples):
            for b in samples:
                total_tests += 1
                result = operation(a, b)
                
                # Check if result is in the original set
                if result not in sample_set:
                    failed_tests += 1
                    results["passed"] = False
                    if failed_tests <= 5:  # Limit failure examples
                        results["failures"].append({
                            "a": a, "b": b, "result": result
                        })
        
        results["total_tests"] = total_tests
        results["failed_tests"] = failed_tests
        results["pass_rate"] = (total_tests - failed_tests) / total_tests if total_tests > 0 else 0
        
        return results

    @staticmethod
    def test_avalanche(
            fn: Callable, 
            inputs: List[Any], 
            bit_flip_positions: List[int] = None
        ) -> Dict:
        """
        Test the avalanche effect: small input changes should cause significant 
        output changes.
        
        Args:
            fn: Function to test
            inputs: List of baseline inputs
            bit_flip_positions: Positions to flip bits in inputs
            
        Returns:
            Dict containing avalanche test results
        """
        if bit_flip_positions is None:
            bit_flip_positions = [0, 4, 8, 16, 32, 64]
            
        results = {
            "property": "avalanche", 
            "passed": False,  # Will be set based on threshold
            "bit_positions": {},
            "summary": {}
        }
        
        all_differences = []
        
        for pos in bit_flip_positions:
            results["bit_positions"][pos] = {
                "samples": [],
                "differences": []
            }
            
            for input_val in inputs:
                # Create modified input with a single bit flipped
                modified = MathProperties._flip_bit(input_val, pos)
                
                # Get outputs for original and modified inputs
                orig_output = fn(input_val)
                mod_output = fn(modified)
                
                # Calculate difference between outputs (in bits)
                diff = MathProperties._bit_difference(orig_output, mod_output)
                diff_percent = diff * 100
                
                results["bit_positions"][pos]["differences"].append(diff_percent)
                all_differences.append(diff_percent)
                
                # Save a few sample results
                if len(results["bit_positions"][pos]["samples"]) < 3:
                    results["bit_positions"][pos]["samples"].append({
                        "original": input_val,
                        "modified": modified,
                        "orig_output": orig_output,
                        "mod_output": mod_output,
                        "diff_percent": diff_percent
                    })
            
            # Calculate average difference for this bit position
            avg_diff = np.mean(results["bit_positions"][pos]["differences"])
            results["bit_positions"][pos]["avg_difference"] = avg_diff
        
        # Calculate overall statistics
        results["summary"]["avg_difference"] = np.mean(all_differences)
        results["summary"]["min_difference"] = np.min(all_differences)
        results["summary"]["max_difference"] = np.max(all_differences)
        results["summary"]["std_deviation"] = np.std(all_differences)
        
        # An ideal avalanche effect should change approximately 50% of output bits
        results["passed"] = 40 <= results["summary"]["avg_difference"] <= 60
        
        return results

    @staticmethod
    def _flip_bit(value: Any, position: int) -> Any:
        """
        Flip a bit in the input value at the specified position.
        
        Args:
            value: Input value (can be int, bytes, list, etc.)
            position: Bit position to flip
            
        Returns:
            Value with bit flipped
        """
        if isinstance(value, int):
            return value ^ (1 << position)
        elif isinstance(value, bytes) or isinstance(value, bytearray):
            byte_pos = position // 8
            bit_pos = position % 8
            if byte_pos >= len(value):
                return value
            byte_array = bytearray(value)
            byte_array[byte_pos] ^= (1 << bit_pos)
            return bytes(byte_array)
        elif isinstance(value, list):
            # For lists, interpret position as index
            if position < len(value):
                # For numeric values, flip lowest bit
                if isinstance(value[position], (int, float)):
                    result = value.copy()
                    if isinstance(result[position], int):
                        result[position] ^= 1
                    else:  # float
                        result[position] += 0.1  # Small change for float
                    return result
            return value
        return value  # Default case, return unchanged

    @staticmethod
    def _bit_difference(a: Any, b: Any) -> float:
        """
        Calculate the proportion of bits that differ between two values.
        
        Args:
            a: First value
            b: Second value
            
        Returns:
            Proportion of bits that differ (0.0 to 1.0)
        """
        if isinstance(a, int) and isinstance(b, int):
            # For integers, count differing bits
            xor = a ^ b
            bit_count = a.bit_length() or b.bit_length()
            diff_bits = bin(xor).count('1')
            return diff_bits / max(bit_count, 1)
        elif isinstance(a, bytes) and isinstance(b, bytes):
            # For bytes, ensure equal length by padding shorter one
            length = max(len(a), len(b))
            a_padded = a.ljust(length, b'\x00')
            b_padded = b.ljust(length, b'\x00')
            
            diff_bits = 0
            total_bits = length * 8
            
            for byte_a, byte_b in zip(a_padded, b_padded):
                xor = byte_a ^ byte_b
                diff_bits += bin(xor).count('1')
                
            return diff_bits / total_bits
        elif isinstance(a, list) and isinstance(b, list):
            # For lists, count elements that differ
            length = max(len(a), len(b))
            a_padded = a + [0] * (length - len(a))
            b_padded = b + [0] * (length - len(b))
            
            diff_count = sum(1 for x, y in zip(a_padded, b_padded) if x != y)
            return diff_count / length
        
        # Default case
        return 0.0 if a == b else 1.0
