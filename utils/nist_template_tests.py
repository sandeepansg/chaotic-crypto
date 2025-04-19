"""
Template-based NIST statistical tests.
Implements Non-overlapping and Overlapping Template Matching Tests.
"""
import math
import numpy as np
import scipy.special as spc
from typing import Dict, List, Any


class TemplateTests:
    """
    Implementation of template-based statistical tests from NIST SP 800-22.
    """
    
    @staticmethod
    def _generate_templates(m: int):
        """Generate all possible templates of length m."""
        if m == 1:
            return [[0], [1]]
        else:
            templates = []
            sub_templates = TemplateTests._generate_templates(m - 1)
            for template in sub_templates:
                templates.append(template + [0])
                templates.append(template + [1])
            return templates
    
    @staticmethod
    def non_overlapping_template_test(bits: List[int], template: List[int] = None, 
                                   m: int = 9, block_size: int = 8192,
                                   significance_level: float = 0.01) -> Dict[str, Any]:
        """
        Non-overlapping Template Matching Test - tests for occurrences of non-overlapping
        pre-specified templates.
        
        Args:
            bits: Binary sequence as list of bits
            template: Template pattern (if None, a template of all ones is used)
            m: Length of template if template is not specified
            block_size: Size of blocks to analyze
            significance_level: Alpha threshold for P-value
            
        Returns:
            dict: Test results including P-value and success status
        """
        n = len(bits)
        
        # Use default template if none provided
        if template is None:
            template = [1] * m
        else:
            m = len(template)
            
        # Check parameters
        if m < 1 or m > 16:
            return {
                "name": "Non-overlapping Template Test",
                "p_value": 0.0,
                "success": False,
                "error": f"Invalid template length: {m}"
            }
            
        if block_size < 8 * m:
            return {
                "name": "Non-overlapping Template Test",
                "p_value": 0.0,
                "success": False,
                "error": f"Block size must be at least 8 times template length"
            }
            
        # Number of blocks to analyze
        N = n // block_size
        
        if N < 5:
            return {
                "name": "Non-overlapping Template Test",
                "p_value": 0.0,
                "success": False,
                "error": f"Insufficient blocks: need at least 5, got {N}"
            }
            
        # Expected mean for chi-square (asymptotic approximation)
        # μ = (block_size - m + 1) / 2^m
        mean = (block_size - m + 1) / (2**m)
        
        # Expected variance
        variance = block_size * ((1/2**m) * (1 - (1/2**m)))
        
        # Count matches in each block
        W = np.zeros(N)
        
        for i in range(N):
            # Extract current block
            block = bits[i * block_size:(i + 1) * block_size]
            
            # Search for non-overlapping matches
            position = 0
            while position <= block_size - m:
                match = True
                for j in range(m):
                    if block[position + j] != template[j]:
                        match = False
                        break
                
                if match:
                    W[i] += 1
                    position += m  # Skip the entire matched template
                else:
                    position += 1
        
        # Calculate test statistic
        chi_squared = np.sum(((W - mean)**2) / variance)
        
        # Calculate P-value
        p_value = spc.gammaincc(N/2, chi_squared/2)
        
        return {
            "name": "Non-overlapping Template Test",
            "p_value": p_value,
            "success": p_value >= significance_level,
            "chi_squared": chi_squared,
            "template": template,
            "template_length": m,
            "num_blocks": N,
            "block_size": block_size,
            "mean": mean,
            "variance": variance
        }
    
    @staticmethod
    def overlapping_template_test(bits: List[int], m: int = 9, block_size: int = 1032,
                              significance_level: float = 0.01) -> Dict[str, Any]:
        """
        Overlapping Template Matching Test - tests for occurrences of overlapping 
        all-ones templates.
        
        Args:
            bits: Binary sequence as list of bits
            m: Length of template (all ones)
            block_size: Size of blocks to analyze
            significance_level: Alpha threshold for P-value
            
        Returns:
            dict: Test results including P-value and success status
        """
        n = len(bits)
        
        # Check parameters
        if m < 1 or m > 16:
            return {
                "name": "Overlapping Template Test",
                "p_value": 0.0,
                "success": False,
                "error": f"Invalid template length: {m}"
            }
            
        # From NIST recommendations
        if m == 9:
            # For m=9, NIST recommends K=5 and block_size=1032
            K = 5
            block_size = 1032
        elif m == 10:
            K = 6
            block_size = 968
        else:
            # For other template lengths, use an approximation
            K = max(2, min(20, m // 2))  # Number of categories
            # Make block_size large enough for expected occurrences
            block_size = max(100, (2**m) * K)
            
        # Number of blocks
        N = n // block_size
        
        if N < 5:
            return {
                "name": "Overlapping Template Test",
                "p_value": 0.0,
                "success": False,
                "error": f"Insufficient blocks: need at least 5, got {N}"
            }
            
        # All-ones template of length m
        template = [1] * m
        
        # Expected values (λ, η) for the test
        # λ = (block_size - m + 1) / 2^m
        lambda_val = (block_size - m + 1) / (2**m)
        eta = lambda_val / 2
        
        # Theoretical probabilities for Chi-square test
        # These are from the NIST paper for K=5 categories
        # For other K values, these should be recalculated
        if K == 5 and m == 9:
            # NIST SP 800-22 values for m=9, K=5
            pi = [0.364091, 0.185659, 0.139381, 0.100571, 0.210298]
        else:
            # For other cases, calculate using approximate formulas
            pi = []
            sum_prob = 0
            for i in range(K):
                prob = math.exp(-eta) * (eta**i) / math.factorial(i)
                pi.append(prob)
                sum_prob += prob
            
            # Last bin is for K or more occurrences
            pi[K-1] = 1 - sum_prob + pi[K-1]
        
        # Initialize histogram for matches in each block
        v = np.zeros(K + 1)
        
        # Process each block
        for i in range(N):
            # Extract current block
            block = bits[i * block_size:(i + 1) * block_size]
            
            # Count overlapping matches
            count = 0
            for j in range(block_size - m + 1):
                match = True
                for k in range(m):
                    if block[j + k] != template[k]:
                        match = False
                        break
                
                if match:
                    count += 1
            
            # Map count to category
            category = min(count, K)
            v[category] += 1
        
        # Calculate chi-squared
        chi_squared = 0
        for i in range(K):
            expected = N * pi[i]
            chi_squared += ((v[i] - expected)**2) / expected
        
        # Calculate P-value (degrees of freedom = K-1)
        p_value = spc.gammaincc((K-1)/2, chi_squared/2)
        
        return {
            "name": "Overlapping Template Test",
            "p_value": p_value,
            "success": p_value >= significance_level,
            "chi_squared": chi_squared,
            "template_length": m,
            "num_blocks": N,
            "block_size": block_size,
            "categories": K,
            "lambda": lambda_val,
            "eta": eta,
            "observed_frequencies": v[:K].tolist()
        }
