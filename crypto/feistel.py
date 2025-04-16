"""
Block cipher implementation using the hyperchaotic system.
"""
import os
import hashlib
from chaos.chaotic import ChaoticSystem
from utils.random_gen import SecureRandom


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
        padding = bytes([padding_len] * padding_len)
        return data + padding
        
    def _unpad_data(self, data):
        """Remove PKCS#7 padding from data."""
        if not data:
            return b''
            
        padding_len = data[-1]
        if padding_len > len(data) or padding_len > self.block_size:
            return b''  # Invalid padding
            
        # Verify padding consistency
        for i in range(1, padding_len + 1):
            if data[-i] != padding_len:
                return b''  # Invalid padding
                
        return data[:-padding_len]
    
    def _derive_key(self, key):
        """Derive a standardized key from input key or generate from S-box."""
        if key is None:
            # Use S-box as key if none provided
            key_bytes = bytearray(32)
            for i in range(min(32, self.sbox_size)):
                key_bytes[i] = self.sbox[i] % 256
            key = bytes(key_bytes)
        return key
    
    def _generate_keys(self, key):
        """Generate round keys from the main key using the hyperchaotic system."""
        # Hash the provided key
        key_hash = hashlib.sha256(key).digest()
        
        # Convert hash to initial state for hyperchaotic system
        initial_state = []
        for i in range(0, min(20, len(key_hash)), 4):
            value = int.from_bytes(key_hash[i:i+4], byteorder='big')
            # Normalize to [-1, 1] range for the chaotic system
            normalized = (value / (2**32 - 1)) * 2 - 1
            initial_state.append(normalized)
            
        # Ensure we have 5 values (x, y, w, u, v)
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
    
    def _feistel_round_function(self, half_block, round_key, round_num):
        """Apply Feistel network round function transformation."""
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
            
            # Use different mixing functions for different rounds to add complexity
            if round_num % 3 == 0:
                # Rotate right by 1 and XOR with previous byte
                mixed[i] = ((result[i] >> 1) | (result[i] << 7)) & 0xFF
                mixed[i] ^= (result[prev_idx] + round_num) & 0xFF
            elif round_num % 3 == 1:
                # Rotate left by 2 and XOR with next byte
                mixed[i] = ((result[i] << 2) | (result[i] >> 6)) & 0xFF
                mixed[i] ^= (result[next_idx] + round_num) & 0xFF
            else:
                # XOR with neighboring bytes and add round number
                mixed[i] = result[i] ^ result[prev_idx] ^ result[next_idx]
                mixed[i] = (mixed[i] + round_num) & 0xFF
                
        return bytes(mixed)
    
    def _process_block(self, block, round_keys, encrypt=True):
        """Process a single block through the Feistel cipher."""
        # Split the block into left and right halves
        half_size = len(block) // 2
        left_half = bytearray(block[:half_size])
        right_half = bytearray(block[half_size:])
        
        # Apply rounds in proper order based on encryption/decryption
        round_indices = range(self.rounds) if encrypt else range(self.rounds - 1, -1, -1)
        for round_idx in round_indices:
            round_key = round_keys[round_idx]
            
            # Transform right half using Feistel round function
            transformed = self._feistel_round_function(bytes(right_half), round_key, round_idx)
            
            # XOR left half with transformed right half
            new_left = bytearray(len(left_half))
            for i in range(len(left_half)):
                new_left[i] = left_half[i] ^ transformed[i % len(transformed)]
            
            # Swap for next round
            left_half, right_half = right_half, new_left
        
        # Final swap (undo the last swap that occurred in the loop)
        return bytes(right_half) + bytes(left_half)
    
    def encrypt(self, plaintext, key=None):
        """Encrypt plaintext using CBC mode with IV."""
        # Generate a random IV using SecureRandom
        iv = SecureRandom.generate_bytes(self.block_size)
        
        # Derive key (from provided key or S-box)
        key = self._derive_key(key)
            
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
                
            # Process through Feistel cipher
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
            
        # Derive key (from provided key or S-box)
        key = self._derive_key(key)
            
        # Generate round keys from key
        round_keys = self._generate_keys(key)
        
        # Process each block in CBC mode
        blocks = [ciphertext[i:i+self.block_size] 
                 for i in range(0, len(ciphertext), self.block_size)]
        
        plaintext_blocks = []
        prev_block = iv
        
        for block in blocks:
            # Process through Feistel cipher (in decrypt mode)
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
        initial_state = SecureRandom.generate_initial_state(entropy)
        
        # Generate byte sequence
        bytes_sequence = ChaoticSystem.generate_bytes(initial_state, sequence_size)
        
        return bytes_sequence
