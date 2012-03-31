"""
Utilities for manipulating bit strings
"""

import numpy as np

def intForBits(bits):
    """Convert a list of zeros and ones to an integer.
    This is the inverse of bitsForInt.
    
    
    Parameters:
        ints - a list of integers (0 or 1)
    """
    return int("".join(map(str, bits)),2)

def bitsForInt(i,size=None):
    """Convert an integer into a list of ones and zeros.
    This is the inverse of intForBits.
    
    Parameters:
        i - a single integer
        size - [Optional] if present, resulting bits will be padded to size
    """
    bits = map(int, bin(i)[2:])
    if size and len(bits) < size:
        bits = [0]*(size-len(bits)) + bits
    return bits

def intsToBytes(ints):
    """Convert a list of zeros and ones to a list of bytes.
    This is the inverse of bytesToInts.
    
    Parameters:
        ints - a list of integers (0 or 1)
    """
    return [chr(intForBits(ints[i:i+8]))
            for i in range(0,len(ints),8)]

def bytesToInts(bytes):
    """Convert a string of bytes (characters) into a list of ones and zeros.
    This is the inverse of intsToBytes.
    
    Parameters:
        bytes - a string of bytes
    """
    ints = []
    for b in bytes:
        bits = bitsForInt(ord(b), 8)
        ints += bits
    return ints
