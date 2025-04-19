"""
Main entry point for the Chebyshev cryptosystem application with hyperchaotic system.
Uses the simplified APIs from chaos.chaotic and crypto.cryptic modules.
"""
import time
from typing import Dict, Any
from crypto.cryptic import CryptoSystem
from ui.interface import UserInterface


def run_demo():
    """Run a demonstration of the Chebyshev DH exchange and hyperchaotic encryption."""
    ui = UserInterface()

    try:
        # Display header
        ui.show_header()

        # Get parameters from user
        private_bits = ui.get_private_key_length()
        cipher_rounds, cipher_block_size = ui.get_feistel_params()
        sbox_size = ui.get_sbox_params()
        entropy = ui.get_entropy()
        
        # Validate parameters
        params = CryptoSystem.get_security_params(private_bits)
        cipher_params = CryptoSystem.validate_feistel_params(cipher_rounds, cipher_block_size)
        sbox_params = CryptoSystem.validate_sbox_params(sbox_size)
        
        # Display validated parameters
        ui.show_param_info(params)
        
        # Initialize DH system
        start_time = time.time()
        dh = CryptoSystem.create_dh_exchange(private_bits)
        init_time = time.time() - start_time

        # Display system info
        system_info = dh.get_system_info()
        ui.show_system_info(system_info, init_time)

        # Perform key exchange
        start_time = time.time()
        exchange = CryptoSystem.simulate_key_exchange(dh, entropy, entropy + "_bob")
        exchange_time = time.time() - start_time
        ui.show_exchange_results(exchange, exchange_time)

        # Generate S-box from shared secret
        start_time = time.time()
        sbox_gen = CryptoSystem.create_sbox_generator(exchange["alice_shared"], sbox_params["box_size"])
        sbox = sbox_gen.generate_with_avalanche()  # Use avalanche method for better distribution
        sbox_time = time.time() - start_time
        ui.show_sbox_generation(sbox, sbox_time)

        # Create hyperchaotic block cipher
        cipher = CryptoSystem.create_block_cipher(
            sbox, 
            rounds=cipher_params["rounds"], 
            block_size=cipher_params["block_size"]
        )
        cipher_info = cipher.get_cipher_info()
        ui.show_feistel_params(cipher_info)

        # Encrypt and decrypt sample message
        start_time = time.time()
        message = ui.get_sample_message()
        
        # Generate key from shared secret
        key = exchange["alice_shared"].to_bytes(
            (exchange["alice_shared"].bit_length() + 7) // 8,
            byteorder='big'
        )
        
        # Perform encryption/decryption
        ciphertext = CryptoSystem.encrypt_data(cipher, message.encode(), key)
        decrypted = CryptoSystem.decrypt_data(cipher, ciphertext, key)
        
        encryption_time = time.time() - start_time
        ui.show_encryption_results(message, ciphertext, decrypted, encryption_time)

        # Run NIST statistical tests if requested
        nist_options = ui.get_nist_test_options(ciphertext_available=True)
        if nist_options:
            # Import NIST analyzer only when needed
            from utils.nist_analyzer import NISTAnalyzer

            start_time = time.time()
            results = None

            if nist_options.get("test_ciphertext", False):
                # Test the ciphertext data
                ui.show_message("info", f"Testing ciphertext with NIST statistical tests...")
                
                results = NISTAnalyzer.analyze_ciphertext(
                    ciphertext,
                    sample_size=nist_options.get("sample_size"),
                    run_all_tests=nist_options.get("run_all_tests", False)
                )
                ui.show_message("info", f"Testing {results['sequence_size']} bytes of ciphertext...")
            
            elif nist_options.get("test_system", False):
                # Test the hyperchaotic system directly
                ui.show_message("info", f"Testing hyperchaotic system with NIST statistical tests...")
                
                results = NISTAnalyzer.analyze_system(
                    sequence_size=nist_options.get("sequence_size", 10000),
                    skip=nist_options.get("skip", 1000),
                    entropy=entropy,
                    run_all_tests=nist_options.get("run_all_tests", False)
                )
                ui.show_message("info", f"Testing {results['sequence_size']} bytes from hyperchaotic system...")
            
            else:
                # Generate test sequence using cipher
                ui.show_message("info", f"Generating random sequence using cipher...")
                
                test_data = cipher.generate_test_sequence(
                    nist_options.get("sequence_size", 10000), 
                    entropy
                )

                # Analyze the sequence
                results = NISTAnalyzer.analyze_sequence(
                    test_data,
                    run_all_tests=nist_options.get("run_all_tests", False)
                )
                ui.show_message("info", f"Testing {results['sequence_size']} bytes of cipher-generated random data...")

            # Run specific tests if requested
            if nist_options.get("specific_tests", None):
                ui.show_message("info", f"Running specific NIST tests...")
                
                # Get the binary data from the appropriate source
                if results:
                    if "test_data" in locals():
                        binary_data = test_data
                    elif nist_options.get("test_ciphertext", False):
                        binary_data = ciphertext
                    else:
                        # Create a new test sequence
                        binary_data = cipher.generate_test_sequence(
                            nist_options.get("sequence_size", 10000), 
                            entropy
                        )
                    
                    # Run specific tests
                    specific_results = NISTAnalyzer.analyze_with_specific_tests(
                        binary_data,
                        tests=nist_options["specific_tests"],
                        significance_level=nist_options.get("significance_level", 0.01)
                    )
                    
                    # Display detailed results for specific tests
                    ui.show_detailed_nist_results(specific_results)
                    
                    # Update main results with specific test results if needed
                    if not results:
                        results = specific_results

            # Display overall results
            if results:
                analysis_time = time.time() - start_time
                ui.show_nist_test_results(results, analysis_time)
                
                # Offer to save results if available
                if ui.confirm_save_results():
                    save_nist_results(results, ui)

    except KeyboardInterrupt:
        ui.show_message("info", "\nDemo aborted by user.")
    except Exception as e:
        ui.show_error(str(e))


def save_nist_results(results: Dict[str, Any], ui: UserInterface):
    """Save NIST test results to a file."""
    try:
        import json
        from datetime import datetime
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nist_results_{timestamp}.json"
        
        # Convert numpy values to native Python types for JSON serialization
        def convert_numpy(obj):
            if isinstance(obj, (dict, list)):
                return obj
            try:
                import numpy as np
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
            except ImportError:
                pass
            return obj
        
        # Clean up results for JSON serialization
        clean_results = json.loads(json.dumps(results, default=convert_numpy))
        
        # Write to file
        with open(filename, 'w') as f:
            json.dump(clean_results, f, indent=2)
        
        ui.show_message("info", f"Results saved to {filename}")
    except Exception as e:
        ui.show_error(f"Failed to save results: {str(e)}")


if __name__ == "__main__":
    run_demo()
