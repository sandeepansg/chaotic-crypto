"""
Main entry point for the Chebyshev cryptosystem application with hyperchaotic system.
Uses the simplified APIs from chaos.py and crypto.py.
"""
import time
from crypto.cryptic import CryptoSystem
from chaos.chaotic import ChaoticSystem
from ui.interface import UserInterface


def run_demo():
    """Run a demonstration of the Chebyshev DH exchange and hyperchaotic encryption."""
    ui = UserInterface()

    try:
        # Display header
        ui.show_header()

        # Get private key length
        private_bits = ui.get_private_key_length()

        # Show calculated security parameters
        params = CryptoSystem.get_security_params(private_bits)
        ui.show_param_info(params)

        # Get cipher parameters
        cipher_rounds, cipher_block_size = ui.get_feistel_params()
        cipher_params = CryptoSystem.validate_feistel_params(cipher_rounds, cipher_block_size)

        # Get S-box size
        sbox_size = ui.get_sbox_params()
        sbox_params = CryptoSystem.validate_sbox_params(sbox_size)

        # Get entropy
        entropy = ui.get_entropy()
        
        # Initialize DH system with entropy
        start_time = time.time()
        dh = CryptoSystem.create_dh_exchange(private_bits)
        init_time = time.time() - start_time

        # Display system info
        system_info = dh.get_system_info()
        ui.show_system_info(system_info, init_time)

        # Perform key exchange using entropy
        start_time = time.time()
        exchange = CryptoSystem.simulate_key_exchange(dh, entropy, entropy + "_bob")
        exchange_time = time.time() - start_time
        ui.show_exchange_results(exchange, exchange_time)

        # Generate S-box from shared secret using hyperchaotic system
        start_time = time.time()
        sbox_gen = CryptoSystem.create_sbox_generator(exchange["alice_shared"], sbox_params["box_size"])
        sbox = sbox_gen.generate()
        sbox_time = time.time() - start_time
        ui.show_sbox_generation(sbox, sbox_time)

        # Demo hyperchaotic block cipher encryption
        start_time = time.time()
        cipher = CryptoSystem.create_block_cipher(sbox, rounds=cipher_params["rounds"], block_size=cipher_params["block_size"])
        
        # Show cipher parameters
        cipher_info = cipher.get_cipher_info()
        ui.show_feistel_params(cipher_info)

        # Get sample message
        message = ui.get_sample_message()

        # Encrypt and decrypt
        ciphertext = CryptoSystem.encrypt_data(cipher, message.encode())
        decrypted = CryptoSystem.decrypt_data(cipher, ciphertext)
        
        encryption_time = time.time() - start_time
        ui.show_encryption_results(message, ciphertext, decrypted, encryption_time)
        
        # NIST statistical tests
        nist_options = ui.get_nist_test_options()
        if nist_options:
            # Only import when needed
            from utils.nist_anals import NISTAnalyzer

            # Run NIST tests on the cipher output
            start_time = time.time()
            
            # Generate test sequence using shared secret as seed
            test_data = cipher.generate_test_sequence(nist_options["sequence_size"], entropy)
            
            # Analyze the sequence
            results = NISTAnalyzer.analyze_sequence(test_data)
            
            # Display results
            analysis_time = time.time() - start_time
            ui.show_nist_test_results(results, analysis_time)

    except KeyboardInterrupt:
        print("\nDemo aborted by user.")
    except Exception as e:
        ui.show_error(str(e))


if __name__ == "__main__":
    run_demo()
