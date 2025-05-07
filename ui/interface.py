"""User interface for the Chebyshev cryptosystem."""
from ui.input_handler import InputHandler
from ui.display_handler import DisplayHandler
from ui.props_ui import PropsUIHandler


class UserInterface:
    """Facade class for UI operations."""

    def __init__(self):
        """Initialize UI components."""
        self.input_handler = InputHandler()
        self.display_handler = DisplayHandler()
        self.props_ui = PropsUIHandler()

    # Input methods
    def get_private_key_length(self):
        """Get private key length."""
        return self.input_handler.get_private_key_length()

    def get_feistel_params(self):
        """Get Feistel cipher parameters."""
        return self.input_handler.get_feistel_params()

    def get_sbox_params(self):
        """Get S-box parameters."""
        return self.input_handler.get_sbox_params()

    def get_entropy(self):
        """Get entropy input."""
        return self.input_handler.get_entropy()

    def get_sample_message(self):
        """Get message to encrypt."""
        return self.input_handler.get_sample_message()

    # Display methods
    def show_header(self):
        """Show application header."""
        self.display_handler.show_header()

    def show_param_info(self, params):
        """Show security parameters."""
        self.display_handler.show_param_info(params)

    def show_system_info(self, system_info, init_time):
        """Show system information."""
        self.display_handler.show_system_info(system_info, init_time)

    def show_feistel_params(self, cipher_info):
        """Show cipher parameters."""
        self.display_handler.show_feistel_params(cipher_info)

    def show_exchange_results(self, results, time_taken):
        """Show key exchange results."""
        self.display_handler.show_exchange_results(results, time_taken)

    def show_sbox_generation(self, sbox, time_taken):
        """Show S-box generation results."""
        self.display_handler.show_sbox_generation(sbox, time_taken)

    def show_encryption_results(self, plaintext, ciphertext, decrypted, time_taken):
        """Show encryption results."""
        self.display_handler.show_encryption_results(plaintext, ciphertext, decrypted, time_taken)

    def show_error(self, error_message):
        """Show error message."""
        self.display_handler.show_message("error", error_message)

    def show_warning(self, warning_message):
        """Show warning message."""
        self.display_handler.show_message("warning", warning_message)

    def show_message(self, msg_type, message):
        """Show message of specified type."""
        self.display_handler.show_message(msg_type, message)

    def confirm_action(self, prompt, default=True):
        """Confirm an action with user."""
        return self.input_handler.confirm_action(prompt, default)

    # Property testing UI methods
    def show_prop_test_menu(self):
        """Show property testing menu."""
        return self.props_ui.show_prop_test_menu()

    def get_chebyshev_test_options(self):
        """Get options for Chebyshev polynomial tests."""
        return self.props_ui.get_chebyshev_test_options()

    def get_hyperchaos_test_options(self):
        """Get options for hyperchaotic system tests."""
        return self.props_ui.get_hyperchaos_test_options()

    def get_crypto_test_options(self):
        """Get options for cryptographic component tests."""
        return self.props_ui.get_crypto_test_options()

    def display_test_results(self, results, test_type):
        """Display test results."""
        self.props_ui.display_test_results(results, test_type)