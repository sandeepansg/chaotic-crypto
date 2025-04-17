"""
Main entry point for the Chebyshev cryptosystem application with hyperchaotic system.
Uses the simplified APIs from chaos.chaotic and crypto.cryptic modules.
"""
import time
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
            from utils.nist_anals import NISTAnalyzer

            start_time = time.time()

            if nist_options.get("test_ciphertext", False):
                # Test the ciphertext data
                results = NISTAnalyzer.analyze_ciphertext(
                    ciphertext,
                    sample_size=nist_options.get("sample_size")
                )
                ui.show_message("info", f"Testing {results['sequence_size']} bytes of ciphertext...")
            else:
                # Generate test sequence using cipher
                test_data = cipher.generate_test_sequence(nist_options["sequence_size"], entropy)

                # Analyze the sequence
                results = NISTAnalyzer.analyze_sequence(test_data)
                ui.show_message("info", f"Testing {results['sequence_size']} bytes of fresh random data...")

            # Display results
            analysis_time = time.time() - start_time
            ui.show_nist_test_results(results, analysis_time)

    except KeyboardInterrupt:
        ui.show_message("info", "\nDemo aborted by user.")
    except Exception as e:
        ui.show_error(str(e))


if __name__ == "__main__":
    run_demo()