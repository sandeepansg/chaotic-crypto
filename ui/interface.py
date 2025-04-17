"""
User interface for the Chebyshev cryptosystem.
Coordinates all user interaction and display components.
"""
from ui.input_handler import InputHandler
from ui.display_handler import DisplayHandler
from ui.nist_io import NISTHandler


class UserInterface:
    """
    Facade class for all UI operations.
    Integrates input and display components.
    """

    def __init__(self):
        """Initialize the user interface components."""
        self.input_handler = InputHandler()
        self.display_handler = DisplayHandler()
        self.nist_handler = NISTHandler()

    # Delegating methods to appropriate handlers
    def show_header(self):
        self.display_handler.show_header()

    def get_private_key_length(self):
        return self.input_handler.get_private_key_length()

    def get_feistel_params(self):
        return self.input_handler.get_feistel_params()

    def get_sbox_params(self):
        return self.input_handler.get_sbox_params()

    def get_entropy(self):
        return self.input_handler.get_entropy()

    def get_sample_message(self):
        return self.input_handler.get_sample_message()

    def get_nist_test_options(self):
        return self.nist_handler.get_nist_test_options()

    def show_param_info(self, params):
        self.display_handler.show_param_info(params)

    def show_system_info(self, system_info, init_time):
        self.display_handler.show_system_info(system_info, init_time)

    def show_feistel_params(self, cipher_info):
        self.display_handler.show_feistel_params(cipher_info)

    def show_exchange_results(self, results, time_taken):
        self.display_handler.show_exchange_results(results, time_taken)

    def show_sbox_generation(self, sbox, time_taken):
        self.display_handler.show_sbox_generation(sbox, time_taken)

    def show_encryption_results(self, plaintext, ciphertext, decrypted, time_taken):
        self.display_handler.show_encryption_results(plaintext, ciphertext, decrypted, time_taken)

    def show_nist_test_results(self, results, time_taken):
        self.nist_handler.show_nist_test_results(results, time_taken)

    def show_error(self, error_message):
        self.display_handler.show_message("error", error_message)

    def show_warning(self, warning_message):
        self.display_handler.show_message("warning", warning_message)
