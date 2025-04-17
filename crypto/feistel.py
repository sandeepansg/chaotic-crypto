"""
Block cipher implementation using the hyperchaotic system.
"""
import os
import hashlib
from chaos.chaotic import ChaoticSystem


class HyperchaosBlockCipher:
    """Block cipher implementation using the hyperchaotic system."""

    def __init__(self, sbox, rounds=16, block_size=8):
        """Initialize the block cipher."""
        self.rounds = rounds
        self.block_size = block_size
        self.half_block_size = self.block_size // 2
        self.sbox = sbox
        self.sbox_size = len(sbox)
        
    def _pad_data(self, data):
        """Pad data to be a multiple of block_size using PKCS#7 padding."""
        padding_len = self.block_size - (len(data) % self.block_size)
        if padding_len == self.block_size:
            padding = bytes([self.block_size] * self.block_size)
        else:
            padding = bytes([padding_len] * padding_len)
        return data + padding
        
    def _unpad_data(self, data):
        """Remove PKCS#7 padding from data."""
        if not data:
            return b''
            
        padding_len = data[-1]
        return data[:-padding_len]
    
    def _generate_keys(self, key):
        """Generate round keys from the main key using the hyperchaotic system."""
        # Hash the provided key
        key_hash = hashlib.sha256(key).digest()
        
        # Convert hash to initial state for hyperchaotic system
        initial_state = []
        for i in range(0, min(20, len(key_hash)), 4):
            value = int.from_bytes(key_hash[i:i+4], byteorder='big')
            normalized = (value / (2**32 - 1)) * 2 - 1
            initial_state.append(normalized)
            
        # Ensure we have 5 values
        while len(initial_state) < 5:
            initial_state.append(0.1)
        
        # Generate block-sized round keys for each round
        round_keys = ChaoticSystem.generate_block(
            initial_state, 
            self.half_block_size, 
            num_blocks=self.rounds,
            skip=200
        )
        
        return round_keys
    
    def _hyperchaotic_round(self, half_block, round_key, round_num):
        """Apply hyperchaotic transformation for one round."""
        result = bytearray(len(half_block))
        
        # First XOR with round key
        for i in range(len(half_block)):
            result[i] = half_block[i] ^ round_key[i % len(round_key)]
        
        # Apply S-box substitution
        for i in range(len(result)):
            index = result[i] % self.sbox_size
            result[i] = self.sbox[index] & 0xFF
        
        # Apply additional mixing based on round number
        mixed = bytearray(len(result))
        for i in range(len(result)):
            prev_idx = (i - 1) % len(result)
            next_idx = (i + 1) % len(result)
            
            if round_num % 3 == 0:
                mixed[i] = ((result[i] >> 1) | (result[i] << 7)) & 0xFF
                mixed[i] ^= (result[prev_idx] + round_num) & 0xFF
            elif round_num % 3 == 1:
                mixed[i] = ((result[i] << 2) | (result[i] >> 6)) & 0xFF
                mixed[i] ^= (result[next_idx] + round_num) & 0xFF
            else:
                mixed[i] = result[i] ^ result[prev_idx] ^ result[next_idx]
                mixed[i] = (mixed[i] + round_num) & 0xFF
                
        return bytes(mixed)
    
    def _process_block(self, block, round_keys, encrypt=True):
        """Process a single block through the cipher."""
        # Split the block into left and right halves
        half_size = len(block) // 2
        L = bytearray(block[:half_size])
        R = bytearray(block[half_size:])
        
        # Apply rounds
        key_sequence = range(self.rounds) if encrypt else range(self.rounds - 1, -1, -1)
        for round_num in key_sequence:
            round_key = round_keys[round_num]
            
            # Transform right half using hyperchaotic round function
            transformed = self._hyperchaotic_round(bytes(R), round_key, round_num)
            
            # XOR left half with transformed right half
            temp_L = bytearray(len(L))
            for i in range(len(L)):
                temp_L[i] = L[i] ^ transformed[i % len(transformed)]
            
            # Swap for next round
            L, R = R, temp_L
        
        # Final swap (undo the last swap that occurred in the loop)
        return bytes(R) + bytes(L)
    
    def encrypt(self, plaintext, key=None):
        """Encrypt plaintext using CBC mode with IV."""
        # Generate a random IV
        iv = os.urandom(self.block_size)
        
        # Use S-box as key if none provided
        if key is None:
            key_bytes = bytearray(32)
            for i in range(min(32, self.sbox_size)):
                key_bytes[i] = self.sbox[i] % 256
            key = bytes(key_bytes)
            
        # Generate round keys from key
        round_keys = self._generate_keys(key)
        
        # Pad the plaintext
        padded_plaintext = self._pad_data(plaintext)
        
        # Process each block in CBC mode
        blocks = [padded_plaintext[i:i+self.block_size] 
                 for i in range(0, len(padded_plaintext), self.block_size)]
        
        # First block XORed with IV
        prev_block = iv
        ciphertext_blocks = []
        
        for block in blocks:
            # XOR with previous ciphertext block (or IV for first block)
            xored_block = bytearray(self.block_size)
            for i in range(self.block_size):
                xored_block[i] = block[i] ^ prev_block[i]
                
            # Process through hyperchaotic cipher
            encrypted_block = self._process_block(bytes(xored_block), round_keys, encrypt=True)
            ciphertext_blocks.append(encrypted_block)
            prev_block = encrypted_block
            
        # Prepend the IV to the ciphertext
        return iv + b''.join(ciphertext_blocks)
    
    def decrypt(self, ciphertext, key=None):
        """Decrypt ciphertext using CBC mode."""
        # Extract IV
        iv = ciphertext[:self.block_size]
        ciphertext = ciphertext[self.block_size:]
        
        # Handle empty ciphertext after IV
        if not ciphertext:
            return b''
            
        # Use S-box as key if none provided
        if key is None:
            key_bytes = bytearray(32)
            for i in range(min(32, self.sbox_size)):
                key_bytes[i] = self.sbox[i] % 256
            key = bytes(key_bytes)
            
        # Generate round keys from key
        round_keys = self._generate_keys(key)
        
        # Process each block in CBC mode
        blocks = [ciphertext[i:i+self.block_size] 
                 for i in range(0, len(ciphertext), self.block_size)]
        
        plaintext_blocks = []
        prev_block = iv
        
        for block in blocks:
            # Process through hyperchaotic cipher (in decrypt mode)
            decrypted_block = self._process_block(block, round_keys, encrypt=False)
            
            # XOR with previous ciphertext block (or IV for first block)
            plaintext_block = bytearray(len(decrypted_block))
            for i in range(len(decrypted_block)):
                plaintext_block[i] = decrypted_block[i] ^ prev_block[i % len(prev_block)]
                
            plaintext_blocks.append(bytes(plaintext_block))
            prev_block = block
            
        # Combine blocks and remove padding
        return self._unpad_data(b''.join(plaintext_blocks))
        
    def get_cipher_info(self):
        """Get cipher parameters for display purposes."""
        return {
            "rounds": self.rounds,
            "block_size": self.block_size,
            "sbox_size": self.sbox_size
        }
        
    def generate_test_sequence(self, sequence_size, entropy=None):
        """Generate a test sequence for NIST statistical tests."""
        # Create initial state from entropy
        from utils.random_gen import SecureRandom
        initial_state = SecureRandom.generate_initial_state(entropy)
        
        # Generate byte sequence
        bytes_sequence = ChaoticSystem.generate_bytes(initial_state, sequence_size)
        
        return bytes_sequence
