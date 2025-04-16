"""
Display handler for the Chebyshev cryptosystem with hyperchaotic cipher.
Responsible for showing information to the user.
"""
import base64


class DisplayHandler:
    """Handles all display operations and formatting."""

    @staticmethod
    def show_header():
        """Display the application header."""
        print("=" * 80)
        print("Secure Chebyshev Polynomial DH Key Exchange with Hyperchaotic Block Cipher")
        print("=" * 80)
        print("All security parameters will be automatically determined based on private key length")

    @staticmethod
    def show_param_info(params):
        """Display derived security parameters."""
        print("\nAutomatically determined security parameters:")
        for key, value in params.items():
            if key.endswith('_bits'):
                print(f"- {key.replace('_', ' ').title()}: {value} bits")

    @staticmethod
    def show_system_info(system_info, init_time):
        """Display system initialization information."""
        print(f"\nSystem initialized in {init_time:.4f} seconds:")
        print(f"- Prime modulus (hex) = 0x{system_info['mod']:X} ({system_info['mod_bits']} bits)")
        print(f"- Public parameter (hex) = 0x{system_info['param']:X} ({system_info['param_bits']} bits)")
        print(f"- Private key size = {system_info['private_bits']} bits")
        print(f"- Public key size = {system_info['public_bits']} bits")

    @staticmethod
    def show_feistel_params(cipher_info):
        """Display cipher parameters."""
        print("\nHyperchaotic Block Cipher Parameters:")
        print(f"- Cipher type: {cipher_info.get('cipher_type', 'Hyperchaotic Block Cipher')}")
        print(f"- Number of rounds: {cipher_info['rounds']} rounds")
        print(f"- Block size: {cipher_info['block_size']} bytes")
        print(f"- S-box size: {cipher_info['sbox_size']} entries")

    @staticmethod
    def show_exchange_results(results, time_taken):
        """Display key exchange results."""
        print("\n" + "-" * 80)
        print("Key Exchange Results")
        print("-" * 80)

        # Show keys and results
        for party in ['alice', 'bob']:
            print(f"{party.title()} private key (hex): 0x{results[f'{party}_private']:X} ({results[f'{party}_private'].bit_length()} bits)")
            print(f"{party.title()} public key (hex): 0x{results[f'{party}_public']:X} ({results[f'{party}_public'].bit_length()} bits)")
        
        print(f"\nAlice shared secret (hex): 0x{results['alice_shared']:X}")
        print(f"Bob shared secret (hex): 0x{results['bob_shared']:X}")
        print(f"\nShared secrets match: {'Yes' if results['match'] else 'No'}")
        print(f"Exchange completed in {time_taken:.4f} seconds")
        
    @staticmethod
    def show_sbox_generation(sbox, time_taken):
        """Display information about the generated S-box."""
        print("\n" + "-" * 80)
        print("Hyperchaotic S-Box Generation")
        print("-" * 80)
        print(f"S-box of size {len(sbox)} generated in {time_taken:.4f} seconds")
        print(f"First 10 values: {sbox[:10]}")
        if len(sbox) > 20:
            print("...")
            print(f"Last 10 values: {sbox[-10:]}")
        
    @staticmethod
    def show_encryption_results(plaintext, ciphertext, decrypted, time_taken):
        """Display encryption and decryption results."""
        print("\n" + "-" * 80)
        print("Hyperchaotic Encryption/Decryption Demo")
        print("-" * 80)
        print(f"Original message: '{plaintext}'")
        print(f"Ciphertext (base64): {base64.b64encode(ciphertext).decode()}")
        print(f"Decrypted message: '{decrypted.decode()}'")
        print(f"Message successfully recovered: {'Yes' if plaintext == decrypted.decode() else 'No'}")
        print(f"Encryption/decryption completed in {time_taken:.4f} seconds")

    @staticmethod
    def show_message(message_type, message):
        """Display a message to the user with appropriate formatting."""
        type_label = message_type.title()
        print(f"\n{type_label}: {message}")
