import os, filecmp, unittest
from audiosteg import amm

DIR = os.path.dirname(__file__)
TEST_FILE = DIR + "/dbz.wav"
TEST_FILE_TMP = DIR + "/dbz_tmp.wav"

class AMM_Test(unittest.TestCase):

    def test(self):
       wav = amm.wavread(TEST_FILE)
       amm.wavwrite(TEST_FILE_TMP,
                     wav[2],
                     leftStream=wav[0],
                     rightStream=wav[1])
       self.assertTrue(filecmp.cmp(TEST_FILE, TEST_FILE_TMP))
