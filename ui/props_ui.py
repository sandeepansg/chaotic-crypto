"""UI handler for mathematical property testing."""
from ui.display_handler import DisplayHandler
from ui.input_handler import InputHandler


class PropsUIHandler:
    """Handles UI operations for property testing."""

    def __init__(self):
        """Initialize UI components."""
        self.display = DisplayHandler()
        self.input = InputHandler()

    def show_prop_test_menu(self):
        """Show property testing menu."""
        print("\n" + "=" * 80)
        print("Mathematical Property Testing")
        print("=" * 80)
        print("1. Test Chebyshev Polynomial Properties")
        print("2. Test Hyperchaotic System Properties")
        print("3. Test Cryptographic Component Properties")
        print("4. Run All Tests")
        print("0. Back to Main Menu")

        choice = self.input.get_int_input(
            "Select an option:",
            0, 4,
            0
        )
        return choice

    def get_chebyshev_test_options(self):
        """Get options for Chebyshev polynomial tests."""
        print("\n" + "-" * 80)
        print("Chebyshev Polynomial Test Options")
        print("-" * 80)

        test_types = {
            "1": "all",
            "2": "semigroup",
            "3": "commutativity",
            "4": "associativity",
            "5": "avalanche"
        }

        print("Test types:")
        for key, value in test_types.items():
            print(f"{key}. {value.title()}")

        choice = self.input.get_int_input(
            "Select test type:",
            1, 5,
            1
        )

        modulus = self.input.get_int_input(
            "Enter modulus (prime number, or leave blank for default):",
            3, 10000,
            1031
        )

        return {
            "test_type": test_types[str(choice)],
            "modulus": modulus
        }

    def get_hyperchaos_test_options(self):
        """Get options for hyperchaotic system tests."""
        print("\n" + "-" * 80)
        print("Hyperchaotic System Test Options")
        print("-" * 80)

        test_types = {
            "1": "all",
            "2": "avalanche",
            "3": "byte_avalanche",
            "4": "sensitivity"
        }

        print("Test types:")
        for key, value in test_types.items():
            print(f"{key}. {value.replace('_', ' ').title()}")

        choice = self.input.get_int_input(
            "Select test type:",
            1, 4,
            1
        )

        k1 = float(input("Enter k1 parameter (default=1.0): ") or "1.0")
        k2 = float(input("Enter k2 parameter (default=4.0): ") or "4.0")
        k3 = float(input("Enter k3 parameter (default=1.2): ") or "1.2")

        return {
            "test_type": test_types[str(choice)],
            "k1": k1,
            "k2": k2,
            "k3": k3
        }

    def get_crypto_test_options(self):
        """Get options for cryptographic component tests."""
        print("\n" + "-" * 80)
        print("Cryptographic Component Test Options")
        print("-" * 80)

        test_types = {
            "1": "all",
            "2": "sbox_avalanche",
            "3": "cipher_avalanche",
            "4": "dh_sensitivity"
        }

        print("Test types:")
        for key, value in test_types.items():
            print(f"{key}. {value.replace('_', ' ').title()}")

        choice = self.input.get_int_input(
            "Select test type:",
            1, 4,
            1
        )

        kwargs = {}

        if test_types[str(choice)] == "sbox_avalanche":
            kwargs["box_size"] = self.input.get_power_of_two(
                "Enter S-box size:",
                16,
                65536,
                256
            )
        elif test_types[str(choice)] == "cipher_avalanche":
            kwargs["rounds"] = self.input.get_int_input(
                "Enter number of rounds:",
                4,
                100,
                16
            )
            kwargs["block_size"] = self.input.get_int_input(
                "Enter block size (bytes):",
                4,
                64,
                8
            )
        elif test_types[str(choice)] == "dh_sensitivity":
            kwargs["private_bits"] = self.input.get_int_input(
                "Enter private key bit length:",
                8,
                64,
                16
            )

        return {
            "test_type": test_types[str(choice)],
            **kwargs
        }

    def display_test_results(self, results, test_type):
        """Display test results."""
        print("\n" + "=" * 80)
        print(f"{test_type.upper()} TEST RESULTS")
        print("=" * 80)

        self._format_and_display_results(results)

        print("\nPress Enter to continue...")
        input()

    def _format_and_display_results(self, results, indent=0):
        """
        Recursively format and display test results.

        Args:
            results: Dict containing test results
            indent: Current indentation level
        """
        indent_str = "  " * indent

        if isinstance(results, dict):
            for key, value in results.items():
                # Format keys nicely
                display_key = key.replace("_", " ").title()

                # Handle special values
                if key == "passed":
                    status = "✓ PASS" if value else "✗ FAIL"
                    print(f"{indent_str}{display_key}: {status}")
                elif key in ["failures", "samples"]:
                    if value and len(value) > 0:
                        print(f"{indent_str}{display_key}: ({len(value)} items)")
                        # Only show the first item to avoid clutter
                        self._format_and_display_results(value[0], indent + 1)
                elif isinstance(value, (dict, list)):
                    print(f"{indent_str}{display_key}:")
                    self._format_and_display_results(value, indent + 1)
                elif isinstance(value, float):
                    print(f"{indent_str}{display_key}: {value:.4f}")
                else:
                    print(f"{indent_str}{display_key}: {value}")
        elif isinstance(results, list):
            if results and indent < 3:  # Limit recursion depth
                # Just show the first item for lists to avoid excessive output
                print(f"{indent_str}Sample item:")
                self._format_and_display_results(results[0], indent + 1)
            elif indent >= 3:
                print(f"{indent_str}...")