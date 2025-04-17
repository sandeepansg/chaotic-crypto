"""
NIST testing interface for the Chebyshev cryptosystem.
Handles all NIST test related input and output operations.
"""


class NISTHandler:
    """Handles NIST statistical test input and output operations."""
    
    @staticmethod
    def get_nist_test_options(ciphertext_available=False):
        """Get NIST statistical test options."""
        print("\nNIST Statistical Test Configuration")
        print("-" * 30)
        print("NIST tests evaluate the randomness quality of the encryption system.")

        # Ask if user wants to run NIST tests
        run_tests = NISTHandler.confirm_action("Would you like to run NIST statistical tests?", default=False)

        if not run_tests:
            return None

        # Default options
        options = {
            "run_tests": True,
            "test_ciphertext": False,
            "sequence_size": 10000
        }

        # If ciphertext is available, ask if they want to test it
        if ciphertext_available:
            test_ciphertext = NISTHandler.confirm_action(
                "Would you like to test the generated ciphertext instead of a fresh random sequence?",
                default=True
            )
            options["test_ciphertext"] = test_ciphertext

            if test_ciphertext:
                print("The ciphertext will be used for NIST testing.")
                # If they want to test ciphertext, we ask if they want to use all or part
                use_sample = NISTHandler.confirm_action(
                    "Would you like to use only a sample of the ciphertext?",
                    default=True
                )

                if use_sample:
                    default_size = 10000
                    print(f"Enter sample size to test [default={default_size}]")
                    size_input = input(f"Enter sample size [1000-100000, default={default_size}]: ")

                    sample_size = default_size
                    if size_input.strip():
                        try:
                            input_val = int(size_input)
                            if input_val < 1000:
                                print(f"Warning: Value too small. Using minimum of 1000")
                                sample_size = 1000
                            elif input_val > 100000:
                                print(f"Warning: Value too large. Using maximum of 100000")
                                sample_size = 100000
                            else:
                                sample_size = input_val
                        except ValueError:
                            print(f"Invalid input. Using default of {default_size}")

                    options["sample_size"] = sample_size
                else:
                    options["sample_size"] = None  # Use all ciphertext

                return options

        # For standard random sequence generation test
        default_size = 10000
        print(f"Enter sequence size for testing [default={default_size}]")
        print("Note: Larger sizes provide more accurate results but take longer to process")

        size_input = input(f"Enter sequence size [1000-100000, default={default_size}]: ")

        sequence_size = default_size
        if size_input.strip():
            try:
                input_val = int(size_input)
                if input_val < 1000:
                    print(f"Warning: Value too small. Using minimum of 1000")
                    sequence_size = 1000
                elif input_val > 100000:
                    print(f"Warning: Value too large. Using maximum of 100000")
                    sequence_size = 100000
                else:
                    sequence_size = input_val
            except ValueError:
                print(f"Invalid input. Using default of {default_size}")

        options["sequence_size"] = sequence_size
        return options

    @staticmethod
    def show_nist_test_results(results, time_taken):
        """Display NIST statistical test results."""
        print("\n" + "-" * 80)
        print("NIST Statistical Test Results")
        print("-" * 80)

        test_results = results["test_results"]

        # Overall results
        passed = test_results['passed']
        total = test_results['total']
        success_rate = test_results['success_rate'] * 100

        print(f"Tests completed in {time_taken:.4f} seconds")
        print(f"Sequence size: {results['sequence_size']} bytes")
        print(f"Tests passed: {passed}/{total} tests ({success_rate:.1f}%)")
        print(f"Overall assessment: {'PASS' if test_results['overall_success'] else 'FAIL'}")

        # Individual test summaries
        print("\nIndividual Test Results:")
        for name, result in test_results['results'].items():
            test_name = result.get("name", name.replace("_", " ").title())
            success = result.get("success", False)

            result_msg = "PASS" if success else "FAIL"
            print(f"- {test_name}: {result_msg}")

            # Show p-values
            if "p_value" in result:
                print(f"  P-value: {result['p_value']:.6f}")
            elif "p_value1" in result and "p_value2" in result:
                print(f"  P-value1: {result['p_value1']:.6f}")
                print(f"  P-value2: {result['p_value2']:.6f}")

    @staticmethod
    def confirm_action(prompt, default=True):
        """Ask user to confirm an action."""
        yes_choices = ['y', 'yes', 'true', '1']
        no_choices = ['n', 'no', 'false', '0']

        default_str = "Y/n" if default else "y/N"
        response = input(f"{prompt} [{default_str}]: ").strip().lower()

        if not response:
            return default

        if response in yes_choices:
            return True
        if response in no_choices:
            return False

        # Invalid response, return default
        print(f"Invalid input. Using default ({default})")
        return default