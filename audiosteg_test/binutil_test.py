"""
Tests for the binutil submodule
"""

from audiosteg import binutil
from unittest import TestCase
from random import randint,choice
import sys
import math

NUM_TRIALS = 200 # number of times to test each method
MAX_BITS = int(math.log(sys.maxint,2))
BITS = ["0","1"]

class Binutil_Test(TestCase):
    
    @staticmethod
    def generateBitString(size):
        return "".join(["1"] + [choice(BITS) for i in xrange(0,size-1)])
    
    @staticmethod
    def generateString(length):
        return "".join([chr(randint(0,255)) for i in xrange(0,length)])
    
    def testBits(self):
        for i in range(0,NUM_TRIALS):
            bitstring = self.generateBitString(randint(1,MAX_BITS))
            num = int(bitstring,2)
            bits = map(int, bitstring)
            self.assertEqual(binutil.intForBits(binutil.bitsForInt(num)), num)
            self.assertEqual(binutil.bitsForInt(binutil.intForBits(bits)), bits)
    
    def testBytes(self):
        for i in range(0,NUM_TRIALS):
            bits = map(int, self.generateBitString(randint(1,MAX_BITS)*8))
            string = self.generateString(randint(1,MAX_BITS)*8)
            self.assertEqual(binutil.intsToBytes(binutil.bytesToInts(string)), list(string))
            self.assertEqual(binutil.bytesToInts(binutil.intsToBytes(bits)), bits)
    
    def test(self):
        self.testBits()
        self.testBytes()
