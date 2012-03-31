import os, commands
from random import randint, choice

# Location of test wav files
TEST_DIR_WAV = "./test_wav/"
TEST_DIR_MP3 = "./test_mp3/"

# Constants
MAX_MESSAGE_SIZE = .001
TEST_ITERATIONS = 10
TEST_ITERATIONS_MAX = 2

# Temp files
TARGET_AUDIO_FILE =   "/tmp/integration_test_audio_file"
MESSAGE_FILE =        "/tmp/integration_test_msg_file_tmp.txt"
OUTPUT_MESSAGE_FILE = "/tmp/integration_test_decode_file_output.txt"

# Location of the encoder (stegan)
STEGAN_LOCATION = "../stegan"

def cleanup():
    """Clean up the temp files we use for testing

    """
    try:
        os.remove(TARGET_AUDIO_FILE)
        os.remove(MESSAGE_FILE)
        os.remove(OUTPUT_MESSAGE_FILE)
    except OSError:
        pass

def cmd_encode(sourceAudio):
    """Build the command we use for encoding

    Returns the command to be run

    Params:
     source_audio - the carrier audio filename

    """
    return "%s --encode %s %s %s" % \
        (STEGAN_LOCATION, sourceAudio, MESSAGE_FILE, TARGET_AUDIO_FILE)

def cmd_decode():
    """Build the decoding command using the tmp files

    Returns the decoding command to be run as a string

    """
    return "%s --decode %s %s" % \
        (STEGAN_LOCATION, TARGET_AUDIO_FILE, OUTPUT_MESSAGE_FILE)

def get_random_filename(isWav):
    """Pick a random test file, either a wav or mp3

    Returns the filename

    Params:
      isWav - true if we want a random wav file, o/w mp3

    """
    # Pick the appropriate directory
    dir = TEST_DIR_WAV if isWav else TEST_DIR_MP3
    # Then pick a random file
    files = os.listdir(dir)
    return dir + files[randint(0,len(files)-1)]

def get_message_size(f, isMax):
    """Calculate the number of bits we want to encode
    The value is randomized between MAX_MESSAGE_SIZE and (MAX_MESSAGE_SIZE)^2

    Returns an int value

    Params:
     f - the filename to generate the message size based on
     isMax - if we want the message size to be maximum
    """

    # A frame is two hex numbers -- that is, 16 bits
    filesize = os.path.getsize(f)
    max_size = int(MAX_MESSAGE_SIZE * filesize)
    print "Message size {0} {1} of the file's size ({2} bits)"\
        .format(("is" if isMax else "will be up to"), MAX_MESSAGE_SIZE, filesize)
    # If we want a max-size message, we're done
    if isMax:
        return max_size
    else:
        min_size = int(MAX_MESSAGE_SIZE * max_size)
        return randint(min_size, max_size) / 8

def make_message(carrier, isMax):
    """Generate a random hexidecimal message based on the given audio file

    Returns a string of bytes

    Params:
     carrier - the carrier audio filename
     isMax - If we want the message to be the maximum

    """
    size = get_message_size(carrier, isMax)
    print "Generating a random message of size " + str(size)
    return "0b" + "".join([choice(["0","1"]) for i in range(0, size)])

def write_message_file(msg):
    """Write out the given message to the tmp file

    Params:
     msg - The string message to write
    
    """
    f = open(MESSAGE_FILE, "w")
    f.write(msg)
    f.close()
    
def read_decode_output():
    """Read the tmp output file

    Returns the string contents of the file

    """
    f = open(OUTPUT_MESSAGE_FILE, "r")
    contents = f.read()
    f.close()
    return contents

def test(tests, isMax, isWav):
    """Run a randomized test TEST_ITERATIONS times.
    A single test is run by picking a random file, generating
    a random message up to MAX_MESSAGE_SIZE percent of the audio file.

    First it runs the encoding command, and does some tests on the created file
    It then runs the decoding command, and compares the resulting message
    to the original file.

    Params:
     tests - How many tests to run
     isMax - True if we want to test with the max size
     isWav - True if we're testing wav files, false if mp3
    """
    failures = 0
    for x in range(0,tests):
        # Get a audio random file, then make a message from it
        carrier = get_random_filename(isWav)
        print "---\nTesting with carrier file " + carrier + "..."
        msg = make_message(carrier, isMax)
        write_message_file(msg)
        # Shell out the commands
        if not run(cmd_encode(carrier)):
            failures += 1
            continue
        if not run(cmd_decode()):
            failures += 1
            continue
        # Compare the results
        if not (compare_audio_files(carrier) 
                and 
                compare_msgs(msg, read_decode_output())):
            failures += 1
        else:
            print "Success!"
        cleanup()
    return failures

def compare_audio_files(sourceFileName):
    """Compare the given audio file to the audio file with the encoded msg
    Currently only compares filesize

    Returns true if the files were equal
    
    Params:
     sourceFileName - the filename of the original audio file
    """
    print "Comparing the size of the source and target audio files..."
    if not os.path.exists(TARGET_AUDIO_FILE):
        print "Failure!\nThe output file did not exist"
        return 0
    src = file_size(sourceFileName)
    targ = file_size(TARGET_AUDIO_FILE)
    compare = targ == src
    if not compare:
        print "Failure!\nThe audio files had different sizes."
        print sourceFileName + " size " + str(src)
        print "Decoded file size " + str(targ)
    return compare
        
def file_size(f):
    """Return the file size of f

    Returns the file size in bits
    
    Params:
     f - File we're checking
    """
    return os.stat(f).st_size

def compare_msgs(original, decoded):
    """Compare the original message to the one we got from decoding
    Prints out debugging info if they were not equal

    Returns true if the messages were equal, false o/w

    Params:
     original - the message we encoded
     decoded - the message we decoded from the audio file

    """
    print "Comparing the decoded message to the original..."
    compare = (original == decoded)
    if not compare:
        print "Failure!\nThe expected message differed from the decoded message"
        print "Original: {0}".format(int(original, 2))
        print "Decoded:  {0}".format(int(decoded, 2))
    return compare

def run(cmd):
    """Run the given command, and report debugging info if the command failed

    Returns true if the command was successful

    Params:
     cmd - The command to run
    """

    print "!Running cmd: " + cmd
    status = commands.getstatusoutput(cmd)
    # If retval was non-zero
    if status[0]:
        print "Failure!\nThere was an error running the command:"
        print status[1]
    # Return true if retval was zero
    return not status[0]

def runTests(iterations, iterationsMax, isWav):
    """Run test iterations for either wav or mp3 files

    Returns the number of failures
    
    Params:
     iterations - number of iterations to run with random msg sizes
     iterationsMax - number of iterations to run with maximum msg size
     isWav - true if we want to test wav files, o/w tests mp3
    """
    print "*****"
    print "Running " + str(iterations) + " tests with random size messages..."
    fails = test(iterations, False, isWav)
    print "*****"
    print "Running " + str(iterationsMax) + " tests with maximum size messages..."
    fails += test(iterationsMax, True, isWav)
    print "*****"
    return fails;

if __name__ == "__main__":
    # Go!
    print "----- Testing WAVE -----"
    fails = runTests(TEST_ITERATIONS, TEST_ITERATIONS_MAX, True)
    print "\n----- Testing mp3 -----"
    fails += runTests(TEST_ITERATIONS, TEST_ITERATIONS_MAX, False)
    print "Failures: " + str(fails)
    exit(fails)
