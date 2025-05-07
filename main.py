"""Main entry point for Chebyshev cryptosystem with hyperchaotic system."""
import time
from crypto.cryptic import CryptoSystem
from ui.interface import UserInterface
from utils.tests.props.props_main import run_property_tests


def show_main_menu(ui):
    """Show main menu options."""
    print("\n" + "=" * 80)
    print("Chebyshev Cryptosystem with Hyperchaotic Block Cipher")
    print("=" * 80)
    print("1. Run Encryption Demo")
    print("2. Run Mathematical Property Tests")
    print("0. Exit")

    return ui.input_handler.get_int_input(
        "Select an option:",
        0, 2,
        1
    )


def run_demo():
    """Run demo of Chebyshev DH exchange and hyperchaotic encryption."""
    ui = UserInterface()

    try:
        ui.show_header()
        private_bits = ui.get_private_key_length()
        cipher_rounds, cipher_block_size = ui.get_feistel_params()
        sbox_size = ui.get_sbox_params()
        entropy = ui.get_entropy()

        params = CryptoSystem.get_security_params(private_bits)
        cipher_params = CryptoSystem.validate_feistel_params(cipher_rounds, cipher_block_size)
        sbox_params = CryptoSystem.validate_sbox_params(sbox_size)

        ui.show_param_info(params)

        start_time = time.time()
        dh = CryptoSystem.create_dh_exchange(private_bits)
        init_time = time.time() - start_time

        system_info = dh.get_system_info()
        ui.show_system_info(system_info, init_time)

        start_time = time.time()
        exchange = CryptoSystem.simulate_key_exchange(dh, entropy, entropy + "_bob")
        exchange_time = time.time() - start_time
        ui.show_exchange_results(exchange, exchange_time)

        start_time = time.time()
        sbox_gen = CryptoSystem.create_sbox_generator(exchange["alice_shared"], sbox_params["box_size"])
        sbox = sbox_gen.generate_with_avalanche()
        sbox_time = time.time() - start_time
        ui.show_sbox_generation(sbox, sbox_time)

        cipher = CryptoSystem.create_block_cipher(
            sbox,
            rounds=cipher_params["rounds"],
            block_size=cipher_params["block_size"]
        )
        cipher_info = cipher.get_cipher_info()
        ui.show_feistel_params(cipher_info)

        start_time = time.time()
        message = ui.get_sample_message()

        key = exchange["alice_shared"].to_bytes(
            (exchange["alice_shared"].bit_length() + 7) // 8,
            byteorder='big'
        )

        ciphertext = CryptoSystem.encrypt_data(cipher, message.encode(), key)
        decrypted = CryptoSystem.decrypt_data(cipher, ciphertext, key)

        encryption_time = time.time() - start_time
        ui.show_encryption_results(message, ciphertext, decrypted, encryption_time)

    except KeyboardInterrupt:
        ui.show_message("info", "\nDemo aborted by user.")
    except Exception as e:
        ui.show_error(str(e))


def main():
    """Main application entry point."""
    ui = UserInterface()

    while True:
        choice = show_main_menu(ui)

        if choice == 0:
            print("Exiting application. Goodbye!")
            break
        elif choice == 1:
            run_demo()
        elif choice == 2:
            run_property_tests()


if __name__ == "__main__":
    main()