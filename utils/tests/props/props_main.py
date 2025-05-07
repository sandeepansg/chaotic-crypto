"""Main entry point for mathematical property testing."""
from utils.tests.props.props_api import PropTestingAPI
from ui.props_ui import PropsUIHandler


class PropTestingMain:
    """Main class for orchestrating property tests."""

    def __init__(self):
        """Initialize testing components."""
        self.api = PropTestingAPI
        self.ui = PropsUIHandler()

    def run_tests(self):
        """Run property tests based on user input."""
        while True:
            choice = self.ui.show_prop_test_menu()

            try:
                if choice == 0:
                    break
                elif choice == 1:
                    self._run_chebyshev_tests()
                elif choice == 2:
                    self._run_hyperchaos_tests()
                elif choice == 3:
                    self._run_crypto_tests()
                elif choice == 4:
                    self._run_all_tests()
            except KeyboardInterrupt:
                print("\nTest canceled by user.")
            except Exception as e:
                print(f"\nError running tests: {str(e)}")

    def _run_chebyshev_tests(self):
        """Run Chebyshev polynomial tests."""
        options = self.ui.get_chebyshev_test_options()
        results = self.api.test_chebyshev(
            modulus=options["modulus"],
            test_type=options["test_type"]
        )
        self.ui.display_test_results(results, "Chebyshev Polynomial")

    def _run_hyperchaos_tests(self):
        """Run hyperchaotic system tests."""
        options = self.ui.get_hyperchaos_test_options()
        results = self.api.test_hyperchaos(
            k1=options["k1"],
            k2=options["k2"],
            k3=options["k3"],
            test_type=options["test_type"]
        )
        self.ui.display_test_results(results, "Hyperchaotic System")

    def _run_crypto_tests(self):
        """Run cryptographic component tests."""
        options = self.ui.get_crypto_test_options()
        test_type = options.pop("test_type")
        results = self.api.test_crypto(test_type=test_type, **options)
        self.ui.display_test_results(results, "Cryptographic Components")

    def _run_all_tests(self):
        """Run all property tests."""
        results = self.api.run_all_tests()
        self.ui.display_test_results(results, "All Property Tests")


def run_property_tests():
    """Run mathematical property tests."""
    tester = PropTestingMain()
    tester.run_tests()


if __name__ == "__main__":
    run_property_tests()