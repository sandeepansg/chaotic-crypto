"""Input handler for the Chebyshev cryptosystem."""
from crypto.security import SecurityParams


class InputHandler:
    """Handles user inputs and validation."""

    @staticmethod
    def get_int_input(prompt, min_val, max_val, default_val, enforce_even=False):
        """Get integer input with validation."""
        print(prompt)
        value_input = input(f"Enter value [{min_val}-{max_val}, default={default_val}]: ")

        if not value_input.strip():
            return default_val

        try:
            value = int(value_input)
            if value < min_val:
                print(f"Warning: Value too small. Using minimum value of {min_val}")
                value = min_val
            elif value > max_val:
                print(f"Warning: Value too large. Using maximum value of {max_val}")
                value = max_val

            if enforce_even and value % 2 != 0:
                print(f"Adjusting value from {value} to {value+1} to ensure it's even")
                value += 1

            return value
        except ValueError:
            print(f"Invalid input. Using default value of {default_val}")
            return default_val

    @staticmethod
    def get_power_of_two(prompt, min_val, max_val, default_val):
        """Get input and round to nearest power of 2."""
        value = InputHandler.get_int_input(prompt, min_val, max_val, default_val)

        power = 1
        while power < value:
            power *= 2

        if power != value:
            print(f"Adjusting value from {value} to {power} (nearest power of 2)")

        return power

    @staticmethod
    def get_private_key_length():
        """Get private key length from user."""
        print("\nPrivate Key Configuration")
        print("-" * 30)
        return InputHandler.get_int_input(
            "Private key length options:",
            SecurityParams.MIN_PRIVATE_BITS,
            SecurityParams.MAX_PRIVATE_BITS,
            SecurityParams.DEFAULT_PRIVATE_BITS
        )

    @staticmethod
    def get_feistel_params():
        """Get Feistel cipher parameters."""
        print("\nFeistel Cipher Configuration")
        print("-" * 30)

        rounds = InputHandler.get_int_input(
            "Feistel rounds options:",
            SecurityParams.MIN_FEISTEL_ROUNDS,
            100,
            SecurityParams.DEFAULT_FEISTEL_ROUNDS
        )

        block_size = InputHandler.get_int_input(
            "Block size options (bytes):",
            SecurityParams.MIN_BLOCK_SIZE,
            SecurityParams.MAX_BLOCK_SIZE,
            SecurityParams.DEFAULT_BLOCK_SIZE,
            enforce_even=True
        )

        return rounds, block_size

    @staticmethod
    def get_sbox_params():
        """Get S-box parameters."""
        print("\nS-Box Configuration")
        print("-" * 30)

        return InputHandler.get_power_of_two(
            "S-box size options:",
            SecurityParams.MIN_SBOX_SIZE,
            SecurityParams.MAX_SBOX_SIZE,
            SecurityParams.DEFAULT_SBOX_SIZE
        )

    @staticmethod
    def get_entropy():
        """Get entropy for key generation."""
        print("\nEntropy Configuration")
        print("-" * 30)
        print("Enter text to use as additional entropy for key generation.")
        return input("Enter text for additional entropy (optional): ")

    @staticmethod
    def get_sample_message():
        """Get a sample message to encrypt."""
        print("\nMessage Encryption")
        print("-" * 30)
        default_message = "This is a secure message exchanged using Chebyshev polynomials!"
        message = input(f"Enter a message to encrypt [default: '{default_message}']: ")
        return message.strip() if message.strip() else default_message

    @staticmethod
    def confirm_action(prompt, default=True):
        """Ask user to confirm an action."""
        default_str = "Y/n" if default else "y/N"
        response = input(f"{prompt} [{default_str}]: ").strip().lower()

        if not response:
            return default

        if response in ['y', 'yes', 'true', '1']:
            return True
        if response in ['n', 'no', 'false', '0']:
            return False

        print(f"Invalid input. Using default ({default})")
        return default